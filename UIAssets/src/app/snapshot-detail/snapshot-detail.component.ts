import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalService} from "ngx-bootstrap";
import {ActivatedRoute, Router} from "@angular/router";
import {Snapshot, SnapshotList} from "../_model/snapshot";
import {BackendService} from "../_service/backend.service";

@Component({
  templateUrl: './snapshot-detail.component.html',
  styleUrls: ['./snapshot-detail.component.css']
})

export class SnapshotDetailComponent implements OnInit {

  public snapshot: Snapshot;
  public loading: boolean;
  public loadingMessage: string;

  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading snapshot';
  }

  ngOnInit(): void {
    this.getSnapshot();
  }

  getSnapshot() {
    this.loading = true;
    this.activatedRoute.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id != null) {
        this.backendService.getSnapshot(id).subscribe((results: SnapshotList) => {
          this.snapshot = results.objects[0];
          this.loading = false;
        }, (err) => {
          this.notificationService.error('Error', 'Could not get snapshot list');
          this.loading = false;
        });
      }
    });
  }
}
