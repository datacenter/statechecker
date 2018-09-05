import {Component, OnInit, TemplateRef} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {ActivatedRoute, Router} from "@angular/router";
import {ComparisonResult, ComparisonResultList} from "../_model/comparison-result";
import {Comparison, ComparisonList} from "../_model/comparison";
import {BackendService} from "../_service/backend.service";

@Component({
  templateUrl: './comparison-result-detail.component.html',
  styleUrls: ['./comparison-result-detail.component.css']
})

export class ComparisonResultDetailComponent implements OnInit {

  public rows: ComparisonResult[];
  public loading: boolean;
  public loadingMessage: string;
  public comparison: Comparison;
  public key: string;
  public value: string;
  public subkey: string;
  public subvalue: string;
  public type: string;
  public semanticDiff: boolean;
  public includeEqual: boolean;
  public modalRef: BsModalRef;
  public selectedComparisonResult: ComparisonResult;
  public selectedComparisonResultProperties: any[];
  private filter: string;
  private details: any;
  comparisonResultDetailSort:any ;
  comparisonResultDetailemSort:any

  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading comparison result details';
    this.semanticDiff = !this.backendService.prefs.comparisonResult_modified_lineDiffMode;
    this.includeEqual = this.backendService.prefs.comparisonResult_modified_emptyResults;
    this.comparisonResultDetailSort = this.backendService.prefs.comparisonResultDetailSort ;
    this.comparisonResultDetailemSort = this.backendService.prefs.comparisonResultDetailemSort ;
  }

  ngOnInit(): void {
    this.activatedRoute.paramMap.subscribe(params => {
      this.loading = true;
      const id = params.get('id');
      this.key = params.get('key');
      this.value = params.get('value');
      this.subkey = params.get('subkey');
      this.subvalue = params.get('subvalue');
      this.type = params.get('type');
      this.backendService.getComparison(id).subscribe((results: ComparisonList) => {
        this.comparison = results.objects[0];
        this.getComparisonResultDetails();
      }, (err) => {
        this.notificationService.error('Error', 'Could not get comparison');
        this.loading = false;
      });
    });
  }

  onSort(event) {
    this.comparisonResultDetailSort = event.sorts ;
  }

  onemSort(event) {
    this.comparisonResultDetailemSort = event.sorts ;
  }

  getComparisonResultDetails() {
    this.loading = true;
    this.backendService.getComparisonResultsDetails(this.comparison, this.key, this.value, this.subkey, this.subvalue, this.type).subscribe((results: ComparisonResultList) => {
      this.details = results.objects[0][this.type];
      this.filterRows();
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get fabric list');
      this.loading = false;
    });
  }

  public openModal(template: TemplateRef<any>, comparisonResult: ComparisonResult) {
    this.selectedComparisonResult = comparisonResult;
    this.updateSelectedComparisonResultProperties();
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

  public onModeChanged(checked: boolean) {
    this.semanticDiff = checked;
    this.backendService.prefs.comparisonResult_modified_lineDiffMode = !checked ;
  }

  public onIncludeEqual(checked: boolean) {
    this.includeEqual = checked;
    this.backendService.prefs.comparisonResult_modified_emptyResults = checked ;
    this.updateSelectedComparisonResultProperties();
  }

  onFilterChanged(event) {
    if (event.target.value) {
      this.filter = event.target.value.toLowerCase();
    } else {
      this.filter = '';
    }
    this.filterRows();
  }

  private filterRows() {
    const filter = this.filter;
    this.rows = this.details.filter(function (d) {
      return d._key.toLowerCase().indexOf(filter) !== -1 || !filter;
    })
  }

  private updateSelectedComparisonResultProperties() {
    this.selectedComparisonResultProperties = [];
    if (this.type != 'modified') {
      const attributes = Object.keys(this.selectedComparisonResult);
      for (let attribute of attributes) {
        const entry = {'attribute': attribute, 'value': this.selectedComparisonResult[attribute]};
        this.selectedComparisonResultProperties.push(entry);
      }
    } else {
      const modifications = this.selectedComparisonResult.modified;
      for (let modification of modifications) {
        const entry = {
          'attribute': modification['attribute'],
          'value1': modification['value1'],
          'value2': modification['value2']
        };
        this.selectedComparisonResultProperties.push(entry);
      }
      if (this.includeEqual) {
        const equals = this.selectedComparisonResult.equal;
        for (let equal of equals) {
          const entry = {
            'attribute': equal['attribute'],
            'value1': equal['value'],
            'value2': equal['value']
          };
          this.selectedComparisonResultProperties.push(entry);
        }
      }
    }
  }
}
