import {Component, OnInit, TemplateRef} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {Definition, DefinitionList} from "../_model/definition";
import {BackendService} from "../_service/backend.service";

@Component({
  templateUrl: './definition.component.html',
  styleUrls: ['./definition.component.css']
})

export class DefinitionComponent implements OnInit {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  selectedDefinition: Definition;
  definition: Definition;
  definitions: Definition[];
  managedObjects: any[];
  definitionSort:any ;

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService) {
    this.loadingMessage = 'Loading definitions';
    this.definitionSort = this.backendService.prefs.definition_sort ;
  }

  ngOnInit(): void {
    this.getDefinitions();
  }

  onSort(event) {
    this.backendService.prefs.definition_sort = event.sorts ;
  }

  getDefinitions() {
    this.loading = true;
    this.backendService.getDefinitions().subscribe((results: DefinitionList) => {
      this.rows = results.objects;
      this.definitions = results.objects;
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get definition list');
      this.loading = false;
    });
  }

  deleteDefinition() {
    this.loading = true;
    this.modalRef.hide();
    this.backendService.deleteDefinition(this.selectedDefinition).subscribe((results) => {
      this.getDefinitions();
    }, (err) => {
      if (err['error']['error'] !== undefined) {
        this.notificationService.error(err['error']['error']);
        } else {
          this.notificationService.error('Error', 'Could not delete definition') ;
        }
      this.loading = false;
    });
  }

  public onSubmit() {
    this.loading = true;
    this.backendService.createDefinition(this.definition).subscribe((results) => {
      this.getDefinitions();
      this.modalRef.hide();
    }, (err) => {
      if (err['error']['error'] !== undefined){
      this.notificationService.error(err['error']['error']);
      } else {
        this.notificationService.error('Error', 'Could not create definition') ;
      }
      this.loading = false;
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.definitions.filter(function (d) {
      return d.definition.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

  public openAddModal(template: TemplateRef<any>) {
    this.backendService.getManagedObjects().subscribe((managedObjects) => {
      const mos = managedObjects.objects;
      this.managedObjects = [];
      for (const mo of mos) {
        this.managedObjects.push({
          'label': mo.classname + ' - ' + mo.description,
          'value': mo.classname
        });
      }
      this.definition = new Definition();
      this.modalRef = this.modalService.show(template, {
        animated: true,
        keyboard: true,
        backdrop: true,
        ignoreBackdropClick: false,
        class: 'modal-lg',
      });
    }, (err) => {
      this.notificationService.error('Error', 'Could not get managed object list');
    });
  }

  public openModal(template: TemplateRef<any>, definition: Definition) {
    this.selectedDefinition = definition;
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

  public getDefinitionClass(row): any {
    if (row.hasOwnProperty('row') && row['row'].hasOwnProperty('template')) {
      if (row['row']['template'] === true) {
      return ' datatable-header-cell-label' ;
      }
    }
  }
}
