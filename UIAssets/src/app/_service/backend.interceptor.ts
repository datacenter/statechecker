import {catchError, map} from 'rxjs/operators';
import {Injectable} from '@angular/core';
import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpResponse
} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {CookieService} from 'ngx-cookie-service';
import {Router} from '@angular/router';
import {BackendService} from "./backend.service";
import {Observable, throwError} from 'rxjs';

@Injectable()
export class BackendInterceptor implements HttpInterceptor {

  constructor(public router: Router, private cookieService: CookieService, private backendService: BackendService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (environment.app_mode) {
      const initialBody = req.body || {};
      let params;
      let body;
      if (this.backendService.isFileUpload()) {
        this.backendService.setFileUpload(false);
        params = params.set('url', '/api/' + req.url).set('method', 'post');
        body = initialBody;
      } else {
        body = {
          'url': '/api/' + req.urlWithParams,
          'method': req.method,
          'data': initialBody
        }
      }
      req = req.clone({
        setHeaders: {
          'DevCookie': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_token'),
          'APIC-Challenge': this.cookieService.get('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_urlToken')
        },
        body: body,
        url: environment.api_entry,
        params: params,
        method: 'post',
      });
    } else if (environment.login_required) {
      req = req.clone({
        withCredentials: true
      });
    }
    return next.handle(req).pipe(map(resp => {
      if (resp instanceof HttpResponse) {
        return resp;
      }
    }), catchError(err => {
      if (err instanceof HttpErrorResponse && err.status === 401 && localStorage.getItem('isLoggedIn') === 'true') {
        localStorage.removeItem('isLoggedIn');
        if (!environment.app_mode) {
          this.router.navigate(['login']);
        }
      }
      return throwError(err);
    }),);
  }
}
