import {fromEvent as observableFromEvent, merge as observableMerge, Observable, of as observableOf} from 'rxjs';

import {filter, map} from 'rxjs/operators';
import {Component, OnDestroy, OnInit, Renderer2, TemplateRef, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, NavigationEnd, PRIMARY_OUTLET, Router} from '@angular/router';
import {environment} from '../environments/environment';
import {BackendService} from './_service/backend.service';
import {Title} from '@angular/platform-browser';
import {CookieService} from 'ngx-cookie-service';
import {User, UserList} from "./_model/user";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {Version} from "./_model/version";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  encapsulation: ViewEncapsulation.None
})

export class AppComponent implements OnInit, OnDestroy {
  modalRef: BsModalRef;
  isConnected: Observable<boolean>;
  konami: boolean;
  login_required: boolean;
  app_mode = environment.app_mode;
  wait_for_status = environment.wait_for_status;
  private stopListening: () => void;
  breadcrumbs = [];
  cookies_acquired = false;
  app_loaded = false;
  app_status = 'Waiting for tokens';
  version: Version;
  authors = ['Andy Gossett', 'Axel Bodart', 'Hrishikesh Deshpande'];

  constructor(public router: Router, private activatedRoute: ActivatedRoute, private backendService: BackendService,
              private renderer: Renderer2, private titleService: Title, private cookieService: CookieService,
              private modalService: BsModalService) {
    this.stopListening = renderer.listen('window', 'message', this.handleMessage.bind(this));
    this.konami = false;
    this.isConnected = observableMerge(
      observableOf(navigator.onLine),
      observableFromEvent(window, 'online').pipe(map(() => true)),
      observableFromEvent(window, 'offline').pipe(map(() => false))
    );
  }

  shuffleAuthor() {
    var j, x, i;
    for (i = this.authors.length - 1; i > 0; i--) {
      j = Math.floor(Math.random() * (i + 1));
      x = this.authors[i];
      this.authors[i] = this.authors[j];
      this.authors[j] = x;
    }
  }

  ngOnInit() {
    if (this.app_mode) {
      this.app_status = 'Waiting for tokens';
      localStorage.setItem('userRole','0') ;
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
    if (environment.login_required) {
      this.backendService.getUsers().subscribe((results: UserList) => {
      });
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

  public openModal(template: TemplateRef<any>, user: User) {
    this.backendService.getVersion().subscribe((results) => {
      this.version = results;
      this.shuffleAuthor();
      this.modalRef = this.modalService.show(template, {
        animated: true,
        keyboard: true,
        backdrop: true,
        ignoreBackdropClick: false,
        class: 'modal',
      });
    });
  }

  public hideModal() {
    this.modalRef.hide();
  }
}
