from time import sleep
from jinja2 import Template
import subprocess
import json
  
# Opening JSON file
f = open('data.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
def create_pvc_manifest():
    print("ok")
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            f = open(i["pvcname"][j]+".yml", "w")
            tm = Template("""
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
    name: {{ pvcname }}
spec:
    storageClassName: {{ storageclassname }}
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: {{ storageclaim }}
    volumeName: {{ pvname  }}
                                        """)
            msg = tm.render(pvcname=i["pvcname"][j],storageclassname=i["storageclassName"][j],storageclaim=i["storageclaim"][j],pvname=i["pvname"][j])                
            f.write(msg)
            f.close()
    create_pv_manifest()        

def create_pv_manifest():
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            f = open(i["pvname"][j]+".yml", "w")
            tm = Template("""
kind: PersistentVolume
apiVersion: v1
metadata:
    name: {{ pvname }}
    namespace: {{ namespace }}
    labels:
        type: amazonEBS
spec:
    capacity:
      storage: {{ storage }}
    storageClassName: {{ storageclassname }}
    accessModes:
    - ReadWriteOnce
    nodeAffinity:
     required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: topology.kubernetes.io/zone
          operator: In
          values:
          - {{ AZ }}
        - key: topology.kubernetes.io/region
          operator: In
          values:
          - us-east-1

    awsElasticBlockStore:
      volumeID: {{volumeid}}
      fsType: {{fstype}}
                                        """)
            msg = tm.render(pvname=i["pvname"][j],storageclassname=i["storageclassName"][j],storage=i["storage"][j],volumeid=i["volumeId"][j],fstype=i["fstype"][j],namespace=i["ns"],AZ=i['A_zone'][j])                
            f.write(msg)
            f.close()                 
        scale_down(i["ns"],i["kskind"],i["kube_service"])


def scale_down(ns,kskind,kube_service):
        scaledown = Template("kubectl scale {{kskind}} --replicas 0 {{kube_service}}  -n {{namespace}}")
        scaledown_msg = scaledown.render(kskind=kskind,namespace=ns,kube_service=kube_service)
        subprocess.run([scaledown_msg], shell=True, check=True)
        sleep(40)
        delete_pvc()

def delete_pvc():
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            cmdpvc = Template("kubectl delete pvc {{pvcname}} -n {{namespace}}")
            cmdpvc_msg = cmdpvc.render(pvcname=i["pvcname"][j],namespace=i["ns"])
            subprocess.run([cmdpvc_msg], shell=True , check=True)
    sleep(14)
    delete_pv()

def delete_pv():
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            cmdpv = Template("kubectl delete pv {{pvname}} -n {{namespace}}")
            cmdpv_msg = cmdpv.render(pvname=i["pvname"][j],namespace=i["ns"])
            subprocess.run([cmdpv_msg], shell=True , check=True)
    create_pv()

def create_pv():
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            cmdpv = Template("kubectl apply -f {{pvname}}.yml -n {{namespace}}")
            cmdpv_msg = cmdpv.render(pvname=i["pvname"][j],namespace=i["ns"])
            subprocess.run([cmdpv_msg], shell=True , check=True)
    create_pvc()



def create_pvc():
    for i in data['kubernetes']:
        for j in range(len(i["pvcname"])):
            cmdpvc = Template("kubectl apply -f {{pvcname}}.yml -n {{namespace}}")
            cmdpvc_msg = cmdpvc.render(pvcname=i["pvcname"][j],namespace=i["ns"])
            subprocess.run([cmdpvc_msg], shell=True , check=True)
        scaleup(i["ns"],i["kskind"],i["kube_service"],i["replicas"])         

def scaleup(ns,kskind,kube_service,replicas):
        scaleup = Template("kubectl scale {{kskind}} --replicas {{replicas}} {{kube_service}}  -n {{namespace}}")
        scaleup_msg = scaleup.render(kskind=kskind,namespace=ns,replicas=replicas,kube_service=kube_service)
        subprocess.run([scaleup_msg], shell=True , check=True)



create_pvc_manifest()        


