#!/bin/bash

pod=$(kubectl get pod -l service=cart -o jsonpath='{.items[0].metadata.name}')

kubectl cp ../proxy/image/mock_client.py $pod:/opt/server/
kubectl cp ../agent.js $pod:/opt/server
