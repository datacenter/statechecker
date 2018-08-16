import {Injectable} from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpParams,
  HttpRequest,
  HttpResponse
} from '@angular/common/http';
import {Observable} from 'rxjs/Observable';
import {environment} from '../../environments/environment';
import {CookieService} from 'ngx-cookie-service';
import {Router} from '@angular/router';
import {BackendService} from "../_service/backend.service";

@Injectable()
export class BackendInterceptor implements HttpInterceptor {

  constructor(public router: Router, private cookieService: CookieService, private backendService: BackendService) {
  }

  

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    
    if (environment.app_mode) {
      if(this.backendService.getFileUploadMode()) {
        console.log(req) ;
        console.log(req.body);
        const formData = req.body ;
        const reqUrl = '/api/' + req.url ;
        const reqParams = new HttpParams() ;
        reqParams.set('url',reqUrl) ;
        req = req.clone({
          setHeaders: {
            'DevCookie': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_token'),
            'APIC-Challenge': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_urlToken'),
          },body:formData,
          url:environment.api_entry,
          params: reqParams,
          method:'POST'
        })
      } else if(!this.backendService.getFileUploadMode()) {
      const initialUrlWithParams = req.urlWithParams;
      const initialBody = req.body || {};
      const initialMethod = req.method;
      req = req.clone({
        setHeaders: {
          'DevCookie': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_token'),
          'APIC-Challenge': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_urlToken'),
        },
        body: {
          'url': '/api/' + initialUrlWithParams,
          'method': initialMethod,
          'data': initialBody
        },
        params: new HttpParams(),
        url: environment.api_entry,
        method: 'post'
      });
    } else if (environment.login_required) {
      req = req.clone({
        withCredentials: true
      });
    }
  }
    return next.handle(req).map(resp => {
      if (resp instanceof HttpResponse) {
        return resp;
      }
    }).catch(err => {
      if (err instanceof HttpErrorResponse && err.status === 401 && localStorage.getItem('isLoggedIn') === 'true') {
        localStorage.removeItem('isLoggedIn');
        this.router.navigate(['login']);
      }
      return Observable.throw(err);
    });
  
}
}
