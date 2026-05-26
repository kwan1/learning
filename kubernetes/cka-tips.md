# CKA Exam Tips & Tricks

## First 60 Seconds of Every Question

```bash
kubectl config use-context <given-context>   # switch cluster
kn <given-namespace>                          # switch namespace if specified
```

---

## 1. Aliases & Autocomplete

Paste this at the start of every exam session:

```bash
alias k=kubectl
alias kn='kubectl config set-context --current --namespace'
source <(kubectl completion bash)
complete -F __start_kubectl k
export do='--dry-run=client -o yaml'
export now='--force --grace-period=0'
```

Usage:
```bash
k get pods                        # instead of kubectl get pods
kn production                     # switch default namespace
k run nginx --image=nginx $do     # dry run shorthand
k delete pod broken $now          # instant delete, no 30s wait
```

---

## 2. Dry Run — Your Main Weapon

Never write YAML from scratch. Generate it:

```bash
# Pod
k run mypod --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment
k create deployment web --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Service
k expose deployment web --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml

# ConfigMap
k create configmap app-config --from-literal=key=value --dry-run=client -o yaml

# Secret
k create secret generic my-secret --from-literal=password=abc123 --dry-run=client -o yaml

# ServiceAccount
k create serviceaccount app-sa --dry-run=client -o yaml

# Role
k create role pod-reader --verb=get,list,watch --resource=pods --dry-run=client -o yaml

# RoleBinding
k create rolebinding read-pods --role=pod-reader --user=jane --dry-run=client -o yaml

# Job
k create job db-migrate --image=busybox -- echo done --dry-run=client -o yaml

# Ingress
k create ingress web-ingress --rule="web.example.com/=web-svc:80" --dry-run=client -o yaml
```

---

## 3. vim Setup (Critical)

YAML breaks if indentation is wrong. Set this up immediately:

```bash
cat >> ~/.vimrc << 'EOF'
set expandtab
set tabstop=2
set shiftwidth=2
set number
EOF
```

In vim, if you mess up indentation on a block: visually select with `Shift+V` then `>` or `<` to indent/dedent.

---

## 4. Context Switching

Every question is on a different cluster. Always run this first:

```bash
kubectl config use-context <context-given-in-question>
```

Forget this and you're editing the wrong cluster. It's the #1 mistake.

---

## 5. kubectl explain

When you can't remember a field:

```bash
k explain pod.spec.containers.resources
k explain pod.spec.tolerations
k explain pv.spec.persistentVolumeReclaimPolicy
k explain networkpolicy.spec.ingress
```

---

## 6. Get Existing Resource as YAML

When you need to modify something that already exists:

```bash
k get pod broken-pod -o yaml > fix.yaml
# edit fix.yaml
k delete pod broken-pod $now
k apply -f fix.yaml
```

Or directly:
```bash
k edit pod broken-pod   # opens in vim live
```

---

## 7. Instant Debugging

```bash
k describe pod <name>                          # events at the bottom tell you what's wrong
k logs <pod> --previous                        # logs from crashed container
k exec -it <pod> -- sh                         # get a shell
k get events --sort-by='.lastTimestamp'        # cluster-wide events
```

---

## 8. ETCD Backup

Always comes up on the exam:

```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

---

## 9. Node Troubleshooting

SSH into a node and fix kubelet:

```bash
ssh node01
systemctl status kubelet
systemctl restart kubelet
journalctl -u kubelet -n 50   # last 50 lines of logs
```

---

## 10. Static Pods

If asked to create a pod on a specific node, place the manifest here on that node:

```
/etc/kubernetes/manifests/
```

---

## 11. Useful Output Tricks

```bash
k get pods -o wide
k get nodes -o jsonpath='{.items[*].metadata.name}'
k get pods --sort-by='.metadata.creationTimestamp'
```
