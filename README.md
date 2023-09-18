# Introduction

In this project, I aim to deploy an image classification model within a Kubernetes environment. Users can submit images using a POST request to the `/classify` endpoint. Upon submission, the system will respond with a JSON file containing the top five predictions for the image classification.

For enhanced fault tolerance, two models are employed:

1. __Wide Resnet(WR):__ This serves as the primary model. Being a larger model, it requires a substantial number of CPU operations.
2. __Mobilenet:__ This acts as the fallback model. It's a more compact model with fewer CPU operations and is used if the Wide Resnet encounters an exception.

To further bolster the system's resilience, I've prepared two Docker images:

1. The primary image includes both the Wide Resnet and Mobilenet.
2. The secondary image houses only Mobilenet.

With the integration of Kubernetes and the Nginx Ingress Controller, traffic is initially directed to the pods housing the primary image. If any of these pods return an HTTP 500 error or experience a timeout, the Ingress Controller seamlessly redirects the traffic to the pods running the secondary image. As the secondary image is more lightweight and faster, it ensures timely predictions even during peak network activity.

All Docker images undergo a build, test, and publish cycle on DockerHub, facilitated by GitHub Workflows.

# Credits

For testing I use several media files:

1. `tests/images/test_image_1.jpg`. Photo by <a href="https://unsplash.com/@marliesestreefland?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Milli</a> on <a href="https://unsplash.com/photos/2l0CWTpcChI?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
2.  `tests/images/test_image_2.jpg`. Photo by <a href="https://unsplash.com/@alvannee?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Alvan Nee</a> on <a href="https://unsplash.com/photos/ZCHj_2lJP00?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
3. `tests/images/test_image_3.jpg`. Photo by <a href="https://unsplash.com/@corneliusventures?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Cornelius Ventures</a> on <a href="https://unsplash.com/photos/Ak81Vc-kCf4?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText">Unsplash</a>
4. `tests/images/test_image_4.jpg`. A first section of Great Gatsby book saved as test_image_4.jpg to check that my code correctly works with non-image saved as image [Gutenberg Library](https://www.gutenberg.org/cache/epub/64317/pg64317-images.html)
   