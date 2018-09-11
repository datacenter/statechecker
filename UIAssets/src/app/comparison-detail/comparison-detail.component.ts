import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalService} from "ngx-bootstrap";
import {ActivatedRoute, Router} from "@angular/router";
import {Comparison, ComparisonList} from "../_model/comparison";
import {BackendService} from "../_service/backend.service";
import {Snapshot, SnapshotList} from "../_model/snapshot";

@Component({
  templateUrl: './comparison-detail.component.html',
  styleUrls: ['./comparison-detail.component.css']
})

export class ComparisonDetailComponent implements OnInit {

  public comparison: Comparison;
  public loading: boolean;
  public loadingMessage: string;
  public nodeMode: boolean;
  public includeEmpty: boolean;
  public rows;
  private filter: string;
  public isExpanded = false ;
  comparisonDetailSort:any ;

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading comparison';
    this.comparisonDetailSort = this.backendService.prefs.comparisonDetail_sort ;
  }

  ngOnInit(): void {
    this.includeEmpty = this.backendService.prefs.comparisonDetail_emptyResults ;
    this.nodeMode = !this.backendService.prefs.comparisonDetail_classView ;
    this.getComparison();
  }

  onSort(event) {
    this.backendService.prefs.comparisonDetail_sort = event.sorts ;
  }

  getComparison() {
    this.loading = true;
    this.activatedRoute.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id != null) {
        this.backendService.getComparison(id).subscribe((results: ComparisonList) => {
          this.comparison = results.objects[0];
          this.backendService.getSnapshots().subscribe((results: SnapshotList) => {
            let snapshots: Snapshot[] = results.objects;
            for (let snapshot of snapshots) {
              if (snapshot._id == this.comparison.snapshot1) {
                this.comparison.snapshot1_obj = snapshot;
              }
              if (snapshot._id == this.comparison.snapshot2) {
                this.comparison.snapshot2_obj = snapshot;
              }
            }
            this.filterRows();
            this.loading = false;
          }, (err) => {
            this.notificationService.error('Error', 'Could not get snapshot list');
            this.loading = false;
          });
        }, (err) => {
          this.notificationService.error('Error', 'Could not get comparison list');
          this.loading = false;
        });
      }
    });
  }

  filterRows() {
    let rows;
    const filter = this.filter;
    const includeEmpty = this.includeEmpty;
    if (this.nodeMode) {
      rows = this.comparison.total_per_node;
      rows = rows.filter(function (d) {
        return d.node_id == filter || !filter;
      });
    } else {
      rows = this.comparison.total_per_class;
      rows = rows.filter(function (d) {
        return d.classname.toLowerCase().indexOf(filter) !== -1 || !filter;
      });
    }
    this.rows = rows.filter(function (d) {
      return includeEmpty || (d.created > 0 || d.modified > 0 || d.deleted > 0);
    });
  }

  onModeChanged(checked: boolean) {
    this.nodeMode = checked;
    this.backendService.prefs.comparisonDetail_classView = !checked ;
    this.filterRows();
  }

  onIncludeChanged(checked: boolean) {
    this.includeEmpty = checked;
    this.backendService.prefs.comparisonDetail_emptyResults = checked ;
    this.filterRows();
  }

  onFilterChanged(event) {
    this.filter = event.target.value.toLowerCase();
    this.filterRows();
  }

  getNodesCSV(comparison) {
    let nodesCSV = '' ;
    if(comparison.nodes.length === 0) {
      return 'All Nodes' ;
    }
    for(let node of comparison.nodes) {
      nodesCSV += node + ',' ;
    }
    
    return nodesCSV.substring(0,nodesCSV.length - 1) ;
  }

  goToClassDetails(classname) {
    this.backendService.prefs.currentLocation = this.router.url ;
    this.router.navigate(['/managed-object',classname]) ;
  }

}
