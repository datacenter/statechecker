import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalService} from "ngx-bootstrap";
import {BackendService} from "../_service/backend.service";
import {SnapshotList} from "../_model/snapshot";
import {ActivatedRoute, Router} from "@angular/router";
import {ManagedObject, ManagedObjectList} from "../_model/managed-object";

@Component({
  templateUrl: './managed-object-detail.component.html',
  styleUrls: ['./managed-object-detail.component.css']
})

export class ManagedObjectDetailComponent implements OnInit {
  rows;
  loading: boolean;
  loadingMessage: string;
  managedObject: ManagedObject;
  prevRoute:any ;
  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading Managed Object';
    this.prevRoute = this.backendService.prefs.currentLocation ;
  }

  ngOnInit(): void {
    this.getManagedObject();
  }

  getManagedObject() {
    this.loading = true;
    this.activatedRoute.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id != null) {
        this.backendService.getManagedObject(id).subscribe((results: ManagedObjectList) => {
          this.managedObject = results.objects[0];
          this.loading = false;
        }, (err) => {
          this.notificationService.error('Error', 'Could not get managed object list');
          this.loading = false;
        });
      }
    });
  }

  goToPrevRoute() {
    console.log(this.prevRoute) ;
    this.router.navigate([this.prevRoute]) ;
  }

}
