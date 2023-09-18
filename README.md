# Introduction

In this project, I aim to deploy an image classification model within a Kubernetes environment. Users can submit images using a POST request to the `/classify` endpoint. Upon submission, the system will respond with a JSON file containing the top five predictions for the image classification.

For enhanced fault tolerance, two models are employed:

1. __Vision Transformer (VT):__ This serves as the primary model. Being a larger model, it requires a substantial number of CPU operations.
2. __Mobilenet:__ This acts as the fallback model. It's a more compact model with fewer CPU operations and is used if the Vision Transformer encounters an exception.

To further bolster the system's resilience, I've prepared two Docker images:

1. The primary image includes both the Vision Transformer and Mobilenet.
2. The secondary image houses only Mobilenet.

With the integration of Kubernetes and the Nginx Ingress Controller, traffic is initially directed to the pods housing the primary image. If any of these pods return an HTTP 500 error or experience a timeout, the Ingress Controller seamlessly redirects the traffic to the pods running the secondary image. As the secondary image is more lightweight and faster, it ensures timely predictions even during peak network activity.

All Docker images undergo a build, test, and publish cycle on DockerHub, facilitated by GitHub Workflows.