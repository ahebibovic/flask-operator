import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException
import yaml

@kopf.on.create("flaskoperators")
def create_fn(spec, **kwargs):
    name = kwargs["body"]["metadata"]["name"]
    print("Name is %s\n" % name)

    replicas = spec.get('replicas', None)
    if not replicas:
        raise kopf.PermanentError(f"Replicas must be set. Got {replicas!r}.")

    image = spec.get('image', None)
    if not image:
        raise kopf.PermanentError(f"Image must be set. Got {image!r}.")

    doc = yaml.safe_load(f"""
              apiVersion: apps/v1
              kind: Deployment
              metadata:
                name: {name}-deployment
                labels:
                  app: {name}
              spec:
                replicas: {replicas}
                selector:
                  matchLabels:
                    app: {name}
                template:
                  metadata:
                    labels:
                      app: {name}
                  spec:
                    containers:
                    - name: {name}
                      image: {image}
                      ports:
                      - containerPort: {spec.get('port', 5000)}
              """)

    kopf.adopt(doc)

    api = kubernetes.client.AppsV1Api()
    try:
      depl = api.create_namespaced_deployment(namespace=doc['metadata']['namespace'], body=doc)
      return {'children': [depl.metadata.uid]}
    except ApiException as e:
      print("Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e)
      
@kopf.on.delete('flaskoperators')
def delete_fn(**kwargs):
  print(kwargs)


  
    