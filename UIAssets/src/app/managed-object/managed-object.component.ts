import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {BackendService} from "../_service/backend.service";
import {ManagedObject, ManagedObjectList} from "../_model/managed-object";

@Component({
  templateUrl: './managed-object.component.html',
  styleUrls: ['./managed-object.component.css']
})

export class ManagedObjectComponent implements OnInit {
  rows;
  loading: boolean;
  loadingMessage: string;
  managedObjects: ManagedObject[];

  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService) {
    this.loadingMessage = 'Loading Managed Objects';
  }

  ngOnInit(): void {
    this.getManagedObjects();
  }

  getManagedObjects() {
    this.loading = true;
    this.backendService.getManagedObjects().subscribe((results: ManagedObjectList) => {
      this.rows = results.objects;
      this.managedObjects = results.objects;
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get Managed Object list');
      this.loading = false;
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.managedObjects.filter(function (d) {
      return d.classname.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }
}
