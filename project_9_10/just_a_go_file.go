package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"time"
	"github.com/gardener/gardener/pkg/client/core/clientset/versioned"
	apierrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/tools/clientcmd"
)

var (
	ErrLocatingKubeconfig = errors.New("could not locate kubeconfig")
	ErrContextEmpty       = errors.New("context empty or missing")
	WaitInterval          = 30 * time.Second
)

const (
	msgDeleted                 				= `Shoot "%s" was deleted`
	msgErrInShootResourceRead  				= `could not get shoot resource "%s": %w`
	msgResourceNotDeletedYet   				= `Resource "%s/%s" not yet deleted`
)

type checkConditionFunction func(ctx context.Context) (done bool, message string, err error)

type shootDeleteFlags struct {
	kubefilePath   string
	name           string
}

func isShootResourceDeletedFunc(name string, namespace string, resource schema.GroupVersionResource, shootClient dynamic.Interface) checkConditionFunction {
	return func(ctx context.Context) (done bool, message string, err error) {
		_, err = shootClient.Resource(resource).Namespace(namespace).Get(ctx, name, metav1.GetOptions{})
		if err != nil {
			// If the shoot resource is not found, it means it was deleted
			if apierrors.IsNotFound(err) {
				return true, fmt.Sprintf(msgDeleted, name), nil
			}
			// Other error when getting resource
			err = fmt.Errorf(msgErrInShootResourceRead, name, err)
			return false, "", err
		}
		return false, fmt.Sprintf(msgResourceNotDeletedYet, namespace, name), nil
	}
}

func runDeleteDevClusterCommand(ctx context.Context, deleteDevClusterFlags shootDeleteFlags, cli versioned.Interface, shootClient dynamic.Interface) error {
	externalServicesDeletion(ctx, shootClient)
	preShootResourceDeletion(ctx, shootClient, cli)
	return nil
}

func deleteResourceInCuster(ctx context.Context, resource schema.GroupVersionResource, shootClient dynamic.Interface) {
	objects, err := shootClient.Resource(resource).Namespace("").List(ctx, metav1.ListOptions{})
	if apierrors.IsNotFound(err) {
		log.Println("resource: ", resource, " not found")
		return
	}
	if err != nil {
		log.Println("failed to list: ", resource.Resource, err)
		return
	} else {
		for _, object := range objects.Items {
			err = shootClient.Resource(resource).Namespace(object.GetNamespace()).Delete(ctx, object.GetName(), metav1.DeleteOptions{})
			if err != nil {
				log.Println("failed to delete resource: ", object.GetKind(), object.GetName(), "in namespace: ", object.GetNamespace(), err)
				return
			}
			isShootResourceDeletedFunc(object.GetName(), object.GetNamespace(), resource, shootClient)
			log.Println("deleted", resource.Resource, object.GetName())
		}
	}
}

func externalServicesDeletion(ctx context.Context, shootClient dynamic.Interface) {
	gv := schema.GroupVersion{Group: "services.cloud.sap.com", Version: "v1"}
	deleteResourceInCuster(ctx, gv.WithResource("servicebindings"), shootClient)
	deleteResourceInCuster(ctx, gv.WithResource("serviceinstances"), shootClient)
}

func preShootResourceDeletion(ctx context.Context, shootClient dynamic.Interface, cli versioned.Interface) {
	PreDeleteResources(ctx, shootClient, cli)
	defer deleteAPIGWResources(ctx, shootClient)
}

func PreDeleteResources(ctx context.Context, shootClient dynamic.Interface, cli versioned.Interface) {
	deleteIstioResources(ctx, shootClient)
	deleteInstallIstioResources(ctx, shootClient)
	deleteDNSResources(ctx, shootClient)
	deleteAutoScalingResources(ctx, shootClient)
	deleteCertManagerResources(ctx, shootClient)
	deleteCalicoResources(ctx, shootClient)
	deleteSnapshotResources(ctx, shootClient)
	deleteFedResources(ctx, shootClient)
	time.Sleep(time.Minute * 1)
	deleteFedGlooResorces(ctx, shootClient)
	deleteCoreAPIGResources(ctx, shootClient)
}

func deleteIstioResources(ctx context.Context, shootClient dynamic.Interface) {
	istioCRD := [3]string{"gateways", "envoyfilters", "virtualservices"}
	gvIstio := schema.GroupVersion{Group: "networking.istio.io", Version: "v1alpha3"}
	for i := 0; i < len(istioCRD); i++ {
		go deleteResourceInCuster(ctx, gvIstio.WithResource(istioCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}
//this 
func deleteDNSResources(ctx context.Context, shootClient dynamic.Interface) {
	dnsCRD := [2]string{"dnsentries", "dnsproviders"}
	gvDNS := schema.GroupVersion{Group: "dns.gardener.cloud", Version: "v1alpha1"}
	for i := 0; i < len(dnsCRD); i++ {
		go deleteResourceInCuster(ctx, gvDNS.WithResource(dnsCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}

func deleteFedResources(ctx context.Context, shootClient dynamic.Interface) {
	glooCRD := [2]string{"federatedmatchablehttpgateways", "federatedvirtualservices"}
	gvGloo := schema.GroupVersion{Group: "fed.gateway.solo.io", Version: "v1"}
	for i := 0; i < len(glooCRD); i++ {
		go deleteResourceInCuster(ctx, gvGloo.WithResource(glooCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}
// need to add label apigw.btp.sap.com/allow-deletion: true
func deleteCoreAPIGResources(ctx context.Context, shootClient dynamic.Interface) {
	coreApigwCRD := [4]string{"apis", "customdomains", "gateways", "federatedapis"}
	gvCoreAPIGW := schema.GroupVersion{Group: "core.apigw.btp.sap.com", Version: "v1alpha1"}
	for i := 0; i < len(coreApigwCRD); i++ {
		go deleteResourceInCuster(ctx, gvCoreAPIGW.WithResource(coreApigwCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}
// this
func deleteAPIGWResources(ctx context.Context, shootClient dynamic.Interface) {
	apigwCRD := [3]string{"centerswstacks", "edgeswstacks", "softwarecomponents"}
	gvAPIGW := schema.GroupVersion{Group: "apigw.sap.com", Version: "v1alpha1"}
	for i := 0; i < len(apigwCRD); i++ {
		go deleteResourceInCuster(ctx, gvAPIGW.WithResource(apigwCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}

func deleteCertManagerResources(ctx context.Context, shootClient dynamic.Interface) {
	gvCert := schema.GroupVersion{Group: "acme.cert-manager.io", Version: "v1"}
	go deleteResourceInCuster(ctx, gvCert.WithResource("orders"), shootClient)
}

func deleteAutoScalingResources(ctx context.Context, shootClient dynamic.Interface) {
	autoScalingCRD := [2]string{"verticalpodautoscalercheckpoints", "verticalpodautoscalers"}
	gvAutoScaling := schema.GroupVersion{Group: "autoscaling.k8s.io", Version: "v1"}
	for i := 0; i < len(autoScalingCRD); i++ {
		go deleteResourceInCuster(ctx, gvAutoScaling.WithResource(autoScalingCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}

func deleteCalicoResources(ctx context.Context, shootClient dynamic.Interface) {
	calicoCRD := [3]string{"clusterinformations", "felixconfigurations", "ippools"}
	gvCalico := schema.GroupVersion{Group: "crd.projectcalico.org", Version: "v1"}
	for i := 0; i < len(calicoCRD); i++ {
		go deleteResourceInCuster(ctx, gvCalico.WithResource(calicoCRD[i]), shootClient)
		time.Sleep(time.Second * 3)
	}
}

func deleteInstallIstioResources(ctx context.Context, shootClient dynamic.Interface) {
	gvInstallIstio := schema.GroupVersion{Group: "install.istio.io", Version: "v1alpha1"}
	go deleteResourceInCuster(ctx, gvInstallIstio.WithResource("istiooperators"), shootClient)
}

func deleteSnapshotResources(ctx context.Context, shootClient dynamic.Interface) {
	gvSnapshot := schema.GroupVersion{Group: "snapshot.storage.k8s.io", Version: "v1"}
	go deleteResourceInCuster(ctx, gvSnapshot.WithResource("volumesnapshotclasses"), shootClient)
}

func deleteFedGlooResorces(ctx context.Context, shootClient dynamic.Interface) {
	gvFedGloo := schema.GroupVersion{Group: "fed.gloo.solo.io", Version: "v1"}
	go deleteResourceInCuster(ctx, gvFedGloo.WithResource("federatedupstreams"), shootClient)
}


func main() {
	var deleteDevClusterFlags = shootDeleteFlags{}
	deleteDevClusterFlags.kubefilePath = os.Getenv("PROJECT_ROBOT")
	deleteDevClusterFlags.name = os.Getenv("SHOOT_NAME")
	kubeconfig := os.Getenv("KUBECONFIG_FILE")
	config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
	ctx := context.Background()
	if err != nil {
		log.Println(err)
		return 
	}
	gardenerClientset, err := versioned.NewForConfig(config)
	if err != nil {
		log.Println(err)
		return 
	}
	if err != nil {
		log.Println(err)
		return 
	}
	err = runDeleteDevClusterCommand(ctx, deleteDevClusterFlags, gardenerClientset, dynamic.NewForConfigOrDie(config))
	if err != nil {
		log.Println(err)
		return 
	}
}
