import {Component, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, NavigationEnd, PRIMARY_OUTLET, Router} from '@angular/router';
import {Observable} from 'rxjs/Rx' ;
import {environment} from '../environments/environment' ;
import {BackendService} from './_service/backend.service' ;
import {Title} from '@angular/platform-browser' ;
import {CookieService} from 'ngx-cookie-service' ;
import {HttpClient, HttpParams} from '@angular/common/http';
import {NotificationsService} from 'angular2-notifications';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  encapsulation: ViewEncapsulation.None
})

export class AppComponent implements OnInit, OnDestroy {
  isConnected: Observable<boolean>;
  konami: boolean;
  login_required: boolean;
  app_mode = environment.app_mode;
  private stopListening: () => void;
  breadcrumbs = [];
  private id: any;
  cookies_acquired = false ;
  app_loaded = false ;
  app_status = 'Waiting for tokens' ;

  constructor(public router: Router, private activatedRoute: ActivatedRoute, private backendService: BackendService, 
    private renderer: Renderer2, private titleService: Title, private cookieService: CookieService,
  private http: HttpClient, private notificationService: NotificationsService) {
    this.stopListening = renderer.listen('window', 'message', this.handleMessage.bind(this));
    this.konami = false;
    this.isConnected = Observable.merge(
      Observable.of(navigator.onLine),
      Observable.fromEvent(window, 'online').map(() => true),
      Observable.fromEvent(window, 'offline').map(() => false)
    );
  }

  ngOnInit() {
    this.app_mode = environment.app_mode ;
    if(!this.app_mode){
      this.app_status = 'Starting App Components' ;
      this.backendService.getSnapshots().subscribe( ()=>{
        
      } , (error)=>{
        if(error['status'] === 401) {
          this.notificationService.error('Invalid session! Please login !') ;
          this.router.navigate(['login']) ;
        }
      }) 
    } else {
      this.app_status = 'Waiting for tokens' ;
    }
    this.getAppStatus().subscribe((response) => {
      this.app_loaded = true ;
    }, (error) => {
      this.app_status = error['error'] ;
    }) ;
    this.login_required = (localStorage.getItem('isLoggedIn') != 'true' && environment.login_required);
    this.router.events.filter(event => event instanceof NavigationEnd).subscribe(event => {
        this.login_required = (localStorage.getItem('isLoggedIn') != 'true' && environment.login_required);
        this.breadcrumbs = [];
        let currentRoute: ActivatedRoute = this.activatedRoute.root;
        let url: string = '';
        while (currentRoute.children.length > 0) {
          let childrenRoutes: ActivatedRoute[] = currentRoute.children;
          let breadCrumbLabel: string = '';
          childrenRoutes.forEach(route => {
            currentRoute = route;
            if (route.outlet == PRIMARY_OUTLET) {
              const hasData = (route.routeConfig && route.routeConfig.data);
              if (hasData) {
                if (route.snapshot.data.hasOwnProperty('breadcrumb')) {
                  breadCrumbLabel = route.snapshot.data['breadcrumb'];
                }
                let routeURL: string = route.snapshot.url.map(segment => segment.path).join("/");
                url += `/${routeURL}`;
                if (routeURL.length === 0) {
                  route.snapshot.params = {};
                }
                let params = route.snapshot.params;
                let arr = [];
                for (let key in params) {
                  if (params.hasOwnProperty(key)) {
                    arr.push(params[key]);
                  }
                }
                let breadcrumb = {
                  label: breadCrumbLabel,
                  params: arr,
                  url: url
                };
                this.breadcrumbs.push(breadcrumb);
              }
            }
          });
        }
        let title = 'StateChecker / ' + this.breadcrumbs[0]['label'];
        if (this.breadcrumbs[0]['params'].length > 0) {
          title += ' / ' + this.breadcrumbs[0]['params'].join(' / ')
        }
        this.titleService.setTitle(title);
      }
    );
  }

  handleMessage(event: Event) {
    const message = event as MessageEvent;
    if (!environment.app_mode) {
      return ;
    }
    const data = JSON.parse(message.data);
    if (data.hasOwnProperty('token') && data.hasOwnProperty('urlToken')) {
      this.cookieService.set('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_token', data['token']);
      this.cookieService.set('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_urlToken', data['urlToken']);
      if (!this.cookies_acquired) {
      this.cookies_acquired = true ;
      this.app_status = 'Starting App Components' ;
     }
    }
  }

  getAppStatus(): Observable<any> {
    let statusUrl = '/aci/app-status' ;
    if (!environment.app_mode) {
      statusUrl = '/api' + statusUrl ;
    }
    return this.http.get(statusUrl).retryWhen(error => {
      return error.flatMap((error:any) => {
        if (error.status === 400 || error['status'] === 400) {
          if (error.hasOwnProperty('error') && error.error.hasOwnProperty('error')) {
            this.app_status = error['error']['error'] ;
          }
        }
        return Observable.of(error).delay(1000) ;
      }).take(300).concat(Observable.throw({error: 'App loading failed'})) ;
    }) ;
  }

  ngOnDestroy() {
    this.stopListening();
    if (!this.app_mode) {
      localStorage.removeItem('isLoggedIn');
    this.backendService.logout().subscribe(() => {
    });
    }
  }

  logout() {
    localStorage.removeItem('isLoggedIn');
    this.backendService.logout().subscribe(() => {
      this.router.navigate(['login']);
    });
  }

  onKonami() {
    this.konami = true;
  }

  noKonami() {
    this.konami = false;
  }
}
