import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalService} from "ngx-bootstrap";
import {ActivatedRoute, Router} from "@angular/router";
import {ComparisonResult, ComparisonResultList} from "../_model/comparison-result";
import {Page} from "../_model/page";
import {Comparison, ComparisonList} from "../_model/comparison";
import {BackendService} from "../_service/backend.service";

@Component({
  templateUrl: './comparison-result.component.html',
  styleUrls: ['./comparison-result.component.css']
})

export class ComparisonResultComponent implements OnInit {

  public rows: ComparisonResult[];
  public page: Page;
  public loading: boolean;
  public loadingMessage: string;
  public comparison: Comparison;
  public key: string;
  public value: string;
  public includeEmpty: boolean;
  public subtotal_equal: number;
  public subtotal_created: number;
  public subtotal_modified: number;
  public subtotal_deleted: number;
  private sort: any;

  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading comparison results';
    this.includeEmpty = false;
    this.sort = [
      {prop: 'classname', dir: 'asc'},
      {prop: 'node_id', dir: 'asc'}
    ];
  }

  ngOnInit(): void {
    this.loading = true;
    this.page = new Page();
    this.activatedRoute.paramMap.subscribe(params => {
      const id = params.get('id');
      this.key = params.get('key');
      this.value = params.get('value');
      this.backendService.getComparison(id).subscribe((results: ComparisonList) => {
        this.comparison = results.objects[0];
        let subtotals;
        if (this.key === 'class') {
          subtotals = this.comparison.total_per_class;
          for (let subtotal of subtotals) {
            if (subtotal['classname'] === this.value) {
              this.subtotal_equal = subtotal['equal'];
              this.subtotal_created = subtotal['created'];
              this.subtotal_modified = subtotal['modified'];
              this.subtotal_deleted = subtotal['deleted'];
              break;
            }
          }
        } else {
          subtotals = this.comparison.total_per_node;
          for (let subtotal of subtotals) {
            if (subtotal['node_id'] == this.value) {
              this.subtotal_equal = subtotal['equal'];
              this.subtotal_created = subtotal['created'];
              this.subtotal_modified = subtotal['modified'];
              this.subtotal_deleted = subtotal['deleted'];
              break;
            }
          }
        }
        this.getComparisonResults();
      }, (err) => {
        this.notificationService.error('Error', 'Could not get comparison');
        this.loading = false;
      });
    });
  }

  getComparisonResults(setLoading = true) {
    if (setLoading) {
      this.loading = true;
    }
    this.backendService.getComparisonResults(this.comparison, this.page, this.key, this.value, this.includeEmpty, this.sort).subscribe((results: ComparisonResultList) => {
      this.page.totalElements = results.count;
      this.rows = results.objects;
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get comparison list');
      this.loading = false;
    });
  }

  setPage(pageInfo) {
    this.page.pageNumber = pageInfo.offset;
    this.getComparisonResults();
  }

  onIncludeChanged(checked: boolean) {
    this.includeEmpty = checked;
    this.page.pageNumber = 0;
    this.getComparisonResults();
  }

  onSort(event) {
    this.sort = event['sorts'];
    this.getComparisonResults(false);
  }

}
