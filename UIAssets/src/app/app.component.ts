import {fromEvent as observableFromEvent, merge as observableMerge, Observable, of as observableOf} from 'rxjs';

import {filter, map} from 'rxjs/operators';
import {Component, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, NavigationEnd, PRIMARY_OUTLET, Router} from '@angular/router';
import {environment} from '../environments/environment';
import {BackendService} from './_service/backend.service';
import {Title} from '@angular/platform-browser';
import {CookieService} from 'ngx-cookie-service';

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
  wait_for_status = environment.wait_for_status;
  private stopListening: () => void;
  breadcrumbs = [];
  private id: any;
  cookies_acquired = false;
  app_loaded = false;
  app_status = 'Waiting for tokens';

  constructor(public router: Router, private activatedRoute: ActivatedRoute, private backendService: BackendService,
              private renderer: Renderer2, private titleService: Title, private cookieService: CookieService) {
    this.stopListening = renderer.listen('window', 'message', this.handleMessage.bind(this));
    this.konami = false;
    this.isConnected = observableMerge(
      observableOf(navigator.onLine),
      observableFromEvent(window, 'online').pipe(map(() => true)),
      observableFromEvent(window, 'offline').pipe(map(() => false))
    );
  }

  ngOnInit() {
    if (this.app_mode) {
      this.app_status = 'Waiting for tokens';
    } else {
      this.app_status = 'Starting App Components';
    }
    if (this.wait_for_status) {
      this.backendService.getAppStatus().subscribe((response) => {
        this.app_loaded = true;
      }, (error) => {
        this.app_status = error['error'];
      });
    } else {
      this.app_loaded = true;
    }
    this.login_required = (localStorage.getItem('isLoggedIn') != 'true' && environment.login_required);
    this.router.events.pipe(filter(event => event instanceof NavigationEnd)).subscribe(event => {
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
    if (environment.app_mode) {
      const data = JSON.parse(message.data);
      if (data.hasOwnProperty('token') && data.hasOwnProperty('urlToken')) {
        this.cookieService.set('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_token', data['token']);
        this.cookieService.set('app_' + environment.aci_vendor + '_' + environment.aci_appId + '_urlToken', data['urlToken']);
        if (!this.cookies_acquired) {
          this.cookies_acquired = true;
          this.app_status = 'Starting App Components';
        }
      }
    }
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
