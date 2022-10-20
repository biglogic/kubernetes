#!/bin/bash

count=$(cat data.csv | wc -l)
echo $count
for (( c=1; c<$count; c++ ))
do
        ns=$(awk -F"," -v val=$c 'NR==val+1{print$1}' data.csv)
        kube_service=$(awk -F"," -v val=$c 'NR==val+1{print$2}' data.csv)
        pvc_name=$(awk -F"," -v val=$c 'NR==val+1{print$3}' data.csv)
        pvname=$(awk -F"," -v val=$c 'NR==val+1{print$4}' data.csv)
        storage=$(awk -F"," -v val=$c 'NR==val+1{print$5}' data.csv)
        volumeID=$(awk -F"," -v val=$c 'NR==val+1{print$6}' data.csv)
        storageClassName=$(awk -F"," -v val=$c 'NR==val+1{print$7}' data.csv)
        kskind=$(awk -F"," -v val=$c 'NR==val+1{print$8}' data.csv)
        fstype=$(awk -F"," -v val=$c 'NR==val+1{print$9}' data.csv)
	      replicas=$(awk -F"," -v val=$c 'NR==val+1{print$10}' data.csv)

done


scaledown(){
   kubectl scale $kskind --replicas 0 $kube_service -n $ns 
}

deletepvc(){
    kubectl delete pvc $pvc_name
}

createpv(){
cat << EOF > $pvname.yml
        kind: PersistentVolume
        apiVersion: v1
          metadata:
            name: $pvname
            namespace: $ns
            labels:
              type: amazonEBS
        spec:
          capacity:
            storage: $storage
          storageClassName: $storageClassName
          accessModes:
          - ReadWriteOnce
          awsElasticBlockStore:
            volumeID: $volumeID
            fsType: $fstype
EOF

}

createpvc(){
cat << EOF > $pvc_name.yml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: $pvc_name
spec:
  storageClassName: $storageClassName
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: $storage_claim
  volumeName: $pvname
EOF

}


apply_update(){
     kubectl apply -f $pvname.yml -n $ns
     kubectl apply -f $pvc_name.yml -n $ns
}

scaleup(){
  kubectl scale $kskind $ --replicas $replicas $kube_service -n $ns
}


