# Ingress

Configures a basic ingress environment:

- Configures Traefik using its chart:

  <https://github.com/traefik/traefik-helm-chart/tree/master/traefik>
  
- Configures cert-manager using its chart:

  <https://github.com/jetstack/cert-manager/tree/master/deploy/charts/cert-manager>
  
Only one release may be installed, because this creates global resources that may conflict.

## Versions

### 0.1.0

Initial version.
