import {Component, OnInit, TemplateRef} from '@angular/core';
import {NotificationsService} from 'angular2-notifications';
import {BsModalRef, BsModalService} from 'ngx-bootstrap';
import {Snapshot, SnapshotList} from '../_model/snapshot';
import {Fabric} from '../_model/fabric';
import {BackendService} from '../_service/backend.service';
import {Definition} from '../_model/definition';

@Component({
  templateUrl: './snapshot.component.html',
  styleUrls: ['./snapshot.component.css']
})

export class SnapshotComponent implements OnInit {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  selectedSnapshot: Snapshot;
  snapshot: Snapshot;
  fabrics: Fabric[];
  snapshots: Snapshot[];
  definitions: Definition[];

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService) {
    this.loadingMessage = 'Loading snapshots';
  }

  ngOnInit(): void {
    this.getSnapshots();
  }

  getSnapshots() {
    this.loading = true;
    this.backendService.getSnapshots(true).subscribe((results: SnapshotList) => {
      this.snapshots = results.objects;
      this.rows = results.objects;
      this.searchIncompleteSnapshots() ;
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get snapshot list');
      this.loading = false;
    });
  }

  searchIncompleteSnapshots(): void {
    for (let row of this.rows) {
      if ((row['status'] === 'init' || row['progress'] < 1) && row['q'] !== true) {
        this.updateProgress(row['_id']) ;
        row['q'] = true ;
      }
    }

  }

  deleteSnapshot() {
    this.loading = true;
    this.backendService.deleteSnapshot(this.selectedSnapshot).subscribe((results) => {
      this.getSnapshots();
      this.modalRef.hide();
    }, (err) => {
      if (err['error']['error'] !== undefined) {
       this.notificationService.error(err['error']['error']) ;
      }
      this.notificationService.error('Error', 'Could not delete snapshot');
      this.loading = false;
    });
  }

  public onSubmit() {
    this.loading = true;
    this.backendService.createSnapshot(this.snapshot).subscribe((results) => {
      this.getSnapshots();
      this.modalRef.hide();
    }, (err) => {
      this.notificationService.error('Error', err['error']['error']);
      this.loading = false;
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.snapshots.filter(function (d) {
      return d.description.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

  public openAddModal(template: TemplateRef<any>) {
    this.backendService.getFabrics().subscribe((fabrics) => {
      this.backendService.getDefinitions().subscribe((definitions) => {
        this.fabrics = fabrics.objects;
        this.definitions = definitions.objects;
        if (this.fabrics.length > 0) {
        this.snapshot = new Snapshot(this.fabrics[0]);
       } else {
         this.notificationService.error('No fabrics discovered!') ;
         return ;
       }
        this.modalRef = this.modalService.show(template, {
          animated: true,
          keyboard: true,
          backdrop: true,
          ignoreBackdropClick: false,
          class: 'modal-lg',
        });
      }, (err) => {
        this.notificationService.error('Error', 'Could not get definition list');
      });
    }, (err) => {
      this.notificationService.error('Error', 'Could not get fabric list');
    });
  }

  public openModal(template: TemplateRef<any>, snapshot: Snapshot) {
    this.selectedSnapshot = snapshot;
    this.modalRef = this.modalService.show(template, {
      animated: true,
      keyboard: true,
      backdrop: true,
      ignoreBackdropClick: false,
      class: 'modal-lg',
    });
  }

  public hideModal() {
    this.modalRef.hide();
  }

  public updateProgress(id: string) {
    if(id === undefined || id === null) {
      return ;
    }
    const notificationService = this.notificationService ;
    const progressSubscription = this.backendService.getProgressFor('snapshots', id).subscribe((response) => {
      if(response['count'] === 0) {
        progressSubscription.unsubscribe() ;
        return ;
      }
      for(let row of this.rows) {
        if(row['_id'] === id) {
          for(let object of response['objects']) {
            if(object['_id'] === id) {
              if(object['status'] === 'error' || object['progress'] === 1) {
                progressSubscription.unsubscribe() ;
              }
              row['status'] = object['status'] ;
              row['progress'] = object['progress'] ;
            }
          }
        }
      }
    } , (error) => {
      this.notificationService.error(error['error']['error']) ;
      progressSubscription.unsubscribe() ;
    }) ;
  }
}
