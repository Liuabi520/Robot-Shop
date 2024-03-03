#!/bin/bash

kubectl exec -it "$(kubectl get pod -l service=cart -o jsonpath='{.items[0].metadata.name}')" -- /bin/bash
