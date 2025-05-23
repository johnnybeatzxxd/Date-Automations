### Create crt
``` python -m seleniumwire extractcert ```

### setup crt
## windows
``` certutil -user -addstore root ./ca.drt ```
## linux
``` certutil -d sql:$HOME/.pki/nssdb -A -t TC -n "Selenium Wire" -i ./ca.crt ```

