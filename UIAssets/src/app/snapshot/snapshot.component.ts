import {Component, OnInit, TemplateRef} from '@angular/core';
import {NotificationsService} from 'angular2-notifications';
import {BsModalRef, BsModalService} from 'ngx-bootstrap';
import {Snapshot, SnapshotList} from '../_model/snapshot';
import {Fabric} from '../_model/fabric';
import {BackendService} from '../_service/backend.service';
import {Definition} from '../_model/definition';
import {environment} from '../../environments/environment';


@Component({
  templateUrl: './snapshot.component.html',
  styleUrls: ['./snapshot.component.css']
})

export class SnapshotComponent implements OnInit {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  fileUploadMessage: string;
  appLoadMessage: string;
  selectedSnapshot: Snapshot;
  snapshot: Snapshot;
  fabrics: Fabric[];
  snapshots: Snapshot[];
  definitions: Definition[];
  app_mode: boolean ;

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService) {
    this.fileUploadMessage = 'Uploading file' ;
    this.appLoadMessage = 'Loading Snapshots' ;
    this.loadingMessage = this.appLoadMessage ;
    this.app_mode = environment.app_mode ;
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
    if (this.app_mode) {
      this.snapshot.fabric = this.fabrics[0].fabric ;
    }
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
       if(this.definitions.length > 0) {
         for(let definition of this.definitions) {
           if(definition.definition.toLowerCase() === 'full' && definition.template === true) {
             this.snapshot.definition = definition.definition
           }
         } 
       }else{
         this.notificationService.error('No definitions found!') ;
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

  fileUploadHandler(event) {
    const reader = new FileReader();
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      if (file.type !== 'application/gzip') {
        this.notificationService.error('Only tgz files supported !') ;
        return ;
      }
      if (file.size > 1073741824) {
        this.notificationService.error('Maximum allowed file size is 1 Gigabyte') ;
        return ;
      }
      const formData = new FormData() ;
      formData.append(file.name, file) ;
      this.loadingMessage = this.fileUploadMessage ;
      this.loading = true ;
      this.backendService.setFileUploadMode(true) ;
      this.backendService.uploadSnapshot(formData).subscribe( (data) => {
        this.loading = false ;
        this.loadingMessage = this.appLoadMessage ;
        this.notificationService.success('File upload complete!') ;
      }, (error) => {
        let msg = 'File Upload Failed !' ;
        if (error['error']['error']) {
          msg = error['error']['error'] ;
        }
        this.notificationService.error(msg) ;
        this.loading = false ;
        this.loadingMessage = this.appLoadMessage ;
      }) ;
  }
  }


  fileDownloadHandler(row) {
    if (row.status === 'complete') {
      this.backendService.downloadSnapshot(row._id, row.filename).subscribe(
        (data) => {
          console.log(data) ;
          const blob = new Blob([data.data], { type: 'application/gzip' });
          const blobUrl = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          document.body.appendChild(a);
          a.setAttribute('style', 'display: none');
          a.href = blobUrl;
          a.download = data.filename;
          a.click();
          window.URL.revokeObjectURL(blobUrl);
          a.remove();
        },
        (error) => {
          this.notificationService.error(error['error']['error']) ;
        }
      ) ;
    } else {
      this.notificationService.error('Snapshot is still being processed') ;
    }
  }
}
