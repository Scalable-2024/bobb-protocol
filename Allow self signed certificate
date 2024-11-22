Setting up SSL for HTTP
Created an ssl_context that disables hostname checking and certificate verification, and also defined a custom SSLAdapter to integrate the ssl_context with the requests library. 
Configured a requests.Session to use the custom SSLAdapter for HTTPS connections and replaced requests.post with session.post to ensure the handshake requests use the custom SSL setup.

This changes were made as pull request but not been implemented in bobb protocol
