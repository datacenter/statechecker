import {Component, OnInit, TemplateRef, OnDestroy} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {Comparison, ComparisonList} from "../_model/comparison";
import {Snapshot, SnapshotList} from "../_model/snapshot";
import {BackendService} from "../_service/backend.service";
import {Definition} from "../_model/definition";

@Component({
  templateUrl: './comparison.component.html',
  styleUrls: ['./comparison.component.css']
})

export class ComparisonComponent implements OnInit, OnDestroy {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  selectedComparison: Comparison;
  comparison: Comparison;
  snapshots: Snapshot[];
  comparisons: Comparison[];
  severities: String[] = ['info', 'notice', 'warn', 'critical', 'error', 'debug'];
  managedObjects: any[];
  definitions: Definition[] ;
  updateQueue: any = [] ;
  predefinedNodes: any = ['global'] ;

  constructor(private backendService: BackendService, private notificationService: NotificationsService, 
    private modalService: BsModalService) {
    this.loadingMessage = 'Loading comparisons';
  }

  ngOnInit(): void {
    this.getComparisons();
  }

  ngOnDestroy(): void {
  }

  getComparisons() {
    this.loading = true;
    this.backendService.getComparisons().subscribe((results: ComparisonList) => {
      let comparisons: Comparison[] = results.objects;
      this.comparisons = comparisons;
      this.rows = comparisons;
      this.loading = false;
      this.searchIncompleteComparisons() ;
      this.backendService.getSnapshots().subscribe((results: SnapshotList) => {
        let snapshots: Snapshot[] = results.objects;
      }, (err) => {
        this.notificationService.error('Error', 'Could not get snapshot list');
        this.loading = false;
      });
    }, (err) => {
      this.notificationService.error('Error', 'Could not get comparison list');
      this.loading = false;
    });
  }

  searchIncompleteComparisons():void {
    for(let row of this.rows) {
      if((row['status'] === 'init' || row['progress'] < 1)&& row['q'] !== true) {
        this.updateProgress(row['_id']) ;
        row['q'] = true ;
      }
    }

  }

  deleteComparison() {
    this.loading = true;
    this.backendService.deleteComparison(this.selectedComparison).subscribe((results) => {
      this.getComparisons();
      this.modalRef.hide();
    }, (err) => {
      this.notificationService.error('Error', 'Could not delete comparison');
      this.loading = false;
    });
  }

  public onSubmit() {
    this.loading = true;
    this.comparison.nodes = this.filterNodes(this.comparison.nodes) ;
    this.backendService.createComparison(this.comparison).subscribe((results) => {
      this.modalRef.hide();
      this.getComparisons();
    }, (err) => {
      this.notificationService.error(err['error']['error']);
      this.loading = false;
    });
  }

  public filterNodes(nodes): any[] {
    let newarr: any[] = [] ;
    for (let i = 0 ; i < nodes.length ; i++) {
     if (typeof(nodes[i]) === 'string') {
       if(nodes[i] === 'global') {
         newarr.push(0) ;
         continue ;
       }
       if (nodes[i].includes(',')) {
         nodes[i] = nodes[i].replace(/\s/g, '') ;
         const csv = nodes[i].split(',') ;
         for ( let j = 0 ; j < csv.length ; j++) {
          if (csv[j].includes('-')) {
            newarr = newarr.concat(this.getArrayForRange(csv[j])) ;
          }
         }
       } else if (nodes[i].includes('-')) {
         newarr = newarr.concat(this.getArrayForRange(nodes[i])) ;
       } else {
         newarr.push(nodes[i]) ;
       }
     }
    }
    return newarr ;
  }

  public getArrayForRange(range: string) {
      const r = range.split('-') ;
      const arr = [] ;
      r.sort() ;
      for (let i = parseInt(r[0], 10) ; i <= parseInt(r[1], 10) ; i ++) {
        arr.push(i) ;
      }
      return arr ;
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.comparisons.filter(function (d) {
      return (d.snapshot1_obj.description.toLowerCase().indexOf(val) !== -1
      || d.snapshot2_obj.description.toLowerCase().indexOf(val) !== -1) || !val;
    });
  }

  onSelectSnapshot(snapshot) {
    this.backendService.getSnapshot(snapshot).subscribe((snapshots) => {
      const snapshot = snapshots.objects[0];
      const definitionName = snapshot.definition;
      this.backendService.getDefinition(definitionName).subscribe((definitions) => {
        const managedObjects = definitions.objects[0].managed_objects;
        this.managedObjects = [];
        for (const managedObject of managedObjects) {
          this.managedObjects.push({'label': managedObject, 'value': managedObject})
        }
      }, (err) => {
        this.notificationService.error('Error', 'Could not get definition');
      });
    }, (err) => {
      this.notificationService.error('Error', 'Could not get snapshot');
    });
  }

  public openAddModal(template: TemplateRef<any>) {
    this.getDefinitions() ;
    this.backendService.getSnapshots().subscribe((snapshots) => {
      this.snapshots = snapshots.objects;
      this.comparison = new Comparison(this.snapshots[0], this.snapshots[0]);
      if (this.snapshots.length > 0) {
      this.onSelectSnapshot(this.snapshots[0]._id);
      this.modalRef = this.modalService.show(template, {
        animated: true,
        keyboard: true,
        backdrop: true,
        ignoreBackdropClick: false,
        class: 'modal-lg',
      });
    } else {
      this.notificationService.error('No snapshots available for comparison') ;
    }
    }, (err) => {
      this.notificationService.error('Error', 'Could not get snapshot list');
    });
  }

  public openModal(template: TemplateRef<any>, comparison: Comparison) {
    this.selectedComparison = comparison;
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

  public getDefinitions() {
    this.backendService.getFabrics().subscribe((fabrics) => {
      this.backendService.getDefinitions().subscribe((definitions) => {
        this.definitions = definitions.objects;
        if (this.definitions.length > 0) {
        this.comparison.definition = this.definitions[0].definition ;
        } else {
          this.notificationService.error('No definitions found!') ;
        }
      }, (err) => {
        this.notificationService.error('Error', 'Could not get definition list');
      });
    });
  }

  public updateProgress(id: string) {
    if(id === undefined || id === null) {
      return ;
    }
    const notificationService = this.notificationService ;
    const progressSubscription = this.backendService.getProgressFor('compare',id).subscribe((response) => {
      if(response['count'] === 0) {
        progressSubscription.unsubscribe() ;
        return ;
      }
      for(let row of this.rows) {
        if(row['_id'] === id) {
          for(let object of response['objects']) {
            if(object['_id'] === id) {
              if(object['status']=== 'error' || object['progress'] === 1) {
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

  addNodes = (term) => {
    return {label: term, value: term} ;
  }
}
