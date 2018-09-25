import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {KonamiModule} from "ngx-konami";
import {RouterModule, Routes} from "@angular/router";
import {SimpleNotificationsModule} from "angular2-notifications";
import {NotFoundComponent} from "./notfound/notfound.component";
import {WelcomeComponent} from "./welcome/welcome.component";
import {HashLocationStrategy, LocationStrategy} from "@angular/common";
import {NgxDatatableModule} from "@swimlane/ngx-datatable";
import {UserComponent} from "./user/user.component";
import {LoadingDotsComponent} from "./common/loading-dots.component";
import {AccordionModule, ModalModule, TooltipModule} from "ngx-bootstrap";
import {DefinitionComponent} from "./definition/definition.component";
import {FabricComponent} from "./fabric/fabric.component";
import {SnapshotComponent} from "./snapshot/snapshot.component";
import {ComparisonComponent} from "./comparison/comparison.component";
import {ComparisonDetailComponent} from "./comparison-detail/comparison-detail.component";
import {ComparisonResultComponent} from "./comparison-result/comparison-result.component";
import {FileSizePipe} from "./common/filesize.pipe";
import {SnapshotDetailComponent} from "./snapshot-detail/snapshot-detail.component";
import {ComparisonResultDetailComponent} from "./comparison-result-detail/comparison-result-detail.component";
import {BackendService} from "./_service/backend.service";
import {BackendInterceptor} from "./_service/backend.interceptor";
import {AuthGuardService} from "./_service/authguard.service";
import {LoginComponent} from "./login/login.component";
import {DefinitionDetailComponent} from "./definition-detail/definition-detail.component";
import {CookieService} from "ngx-cookie-service";
import {ManagedObjectComponent} from "./managed-object/managed-object.component";
import {ManagedObjectDetailComponent} from "./managed-object-detail/managed-object-detail.component";
import {NgSelectModule} from "@ng-select/ng-select";
import {DiffMatchPatchModule} from "ng-diff-match-patch";
import {MomentModule} from "ngx-moment";

const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    data: {breadcrumb: 'Login'}
  },
  {
    path: '',
    canActivate: [AuthGuardService],
    children: [
      {path: '', component: WelcomeComponent, data: {breadcrumb: 'Welcome'}},
      {path: 'users', component: UserComponent, data: {breadcrumb: 'Users'}},
      {path: 'definitions', component: DefinitionComponent, data: {breadcrumb: 'Definitions'}},
      {path: 'definition/:id', component: DefinitionDetailComponent, data: {breadcrumb: 'Definition'}},
      {path: 'fabrics', component: FabricComponent, data: {breadcrumb: 'Fabrics'}},
      {path: 'snapshots', component: SnapshotComponent, data: {breadcrumb: 'Snapshots'}},
      {path: 'snapshot/:id', component: SnapshotDetailComponent, data: {breadcrumb: 'Snapshot'}},
      {path: 'comparisons', component: ComparisonComponent, data: {breadcrumb: 'Comparisons'}},
      {path: 'comparison/:id', component: ComparisonDetailComponent, data: {breadcrumb: 'Comparison'}},
      {path: 'managed-objects', component: ManagedObjectComponent, data: {breadcrumb: 'Managed Objects'}},
      {path: 'managed-object/:id', component: ManagedObjectDetailComponent, data: {breadcrumb: 'Managed Object'}},
      {
        path: 'comparison/:id/results/:key/:value',
        component: ComparisonResultComponent,
        data: {breadcrumb: 'Comparison results'}
      },
      {
        path: 'comparison/:id/results/:key/:value/:type/:subkey/:subvalue',
        component: ComparisonResultDetailComponent,
        data: {breadcrumb: 'Comparison result'}
      },
      {path: '**', component: NotFoundComponent, data: {breadcrumb: 'Error'}},
    ]
  }
];

@NgModule({
  declarations: [
    AppComponent,
    NotFoundComponent,
    UserComponent,
    WelcomeComponent,
    LoginComponent,
    LoadingDotsComponent,
    DefinitionComponent,
    DefinitionDetailComponent,
    FabricComponent,
    SnapshotComponent,
    SnapshotDetailComponent,
    ComparisonComponent,
    ComparisonDetailComponent,
    ComparisonResultComponent,
    ComparisonResultDetailComponent,
    ManagedObjectComponent,
    ManagedObjectDetailComponent,
    FileSizePipe
  ],
  imports: [
    NgSelectModule,
    MomentModule,
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    KonamiModule,
    ModalModule.forRoot(),
    AccordionModule.forRoot(),
    RouterModule.forRoot(routes),
    NgxDatatableModule,
    SimpleNotificationsModule.forRoot(),
    TooltipModule.forRoot(),
    DiffMatchPatchModule
  ],
  providers: [
    CookieService,
    BackendService,
    AuthGuardService,
    {provide: LocationStrategy, useClass: HashLocationStrategy},
    {provide: HTTP_INTERCEPTORS, useClass: BackendInterceptor, multi: true}
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
