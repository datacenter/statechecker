import {Component, OnInit, TemplateRef} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalRef, BsModalService} from "ngx-bootstrap";
import {Fabric, FabricList} from "../_model/fabric";
import {BackendService} from "../_service/backend.service";

@Component({
  templateUrl: './fabric.component.html',
  styleUrls: ['./fabric.component.css']
})

export class FabricComponent implements OnInit {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  selectedFabric: Fabric;
  fabric: Fabric;
  editing = {};
  fabrics: Fabric[];

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService) {
    this.loadingMessage = 'Loading fabrics';
  }

  ngOnInit(): void {
    this.getFabrics(false);
  }

  getFabrics(toBeVerified) {
    this.loading = true;
    this.backendService.getFabrics().subscribe((results: FabricList) => {
      this.fabrics = results.objects;
      this.rows = results.objects;
      const isVerified = this.rows[this.rows.length - 1]['verified'] ;
      if (toBeVerified) {
        this.verifyFabric(this.fabric) ;
      }
      this.loading = false;
    }, (err) => {
      if (err['error']['error'] !== undefined) {
      this.notificationService.error(err['error']['error']) ;
      } else {
      this.notificationService.error('Error', 'Could not get fabric list');
      }
      this.loading = false;
    });
  }

  verifyFabric(fabric: Fabric) {
    this.backendService.verifyFabric(fabric).subscribe((results) => {
      if (results['success']) {
        this.notificationService.success('Success', 'Credentials validated, fetching controllers');
        this.backendService.updateFabricControllers(fabric).subscribe((results) => {
          if (results['success']) {
            this.notificationService.success('Success', 'Controllers fetched');
            this.getFabrics(false);
            this.modalRef.hide();
          } else {
            this.notificationService.error('Error', results['error']);
          }
        }, (err) => {
          this.notificationService.error('Error', 'Could not get controllers');
        });
      } else {
        this.notificationService.error('Error', results['error']);
      }
    }, (err) => {
      this.notificationService.error('Error', 'Could not verify APIC');
    });
  }

  deleteFabric() {
    this.loading = true;
    this.backendService.deleteFabric(this.selectedFabric).subscribe((results) => {
      this.getFabrics(false);
      this.modalRef.hide();
    }, (err) => {
      if (err['error']['error'] !== undefined) {
        this.notificationService.error(err['error']['error']) ;
        } else {
        this.notificationService.error('Error', 'Could not delete fabric');
        }
      this.loading = false;
    });
  }

  public onSubmit() {
    this.loading = true;
    this.backendService.createFabric(this.fabric).subscribe((results) => {
      this.getFabrics(true);
    }, (err) => {
      if (err['error']['error'] !== undefined) {
        this.notificationService.error(err['error']['error']) ;
        } else {
        this.notificationService.error('Error', 'Could not add fabric');
        }
      this.loading = false;
    });
  }

  public updateValue(event, cell, rowIndex) {
    this.editing[rowIndex + '-' + cell] = false;
    if (this.rows[rowIndex][cell] !== event.target.value) {
      this.rows[rowIndex][cell] = event.target.value;
      this.rows = [...this.rows];
      const fabric = this.rows[rowIndex];
      this.backendService.updateFabric(fabric).subscribe((results) => {
        this.notificationService.success('Success', 'Changes saved');
      }, (err) => {
        this.notificationService.error('Error', 'Could not update fabric');
        this.loading = false;
      });
    }
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.fabrics.filter(function (d) {
      return d.fabric.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

  public openAddModal(template: TemplateRef<any>) {
    this.fabric = new Fabric();
    this.modalRef = this.modalService.show(template, {
      animated: true,
      keyboard: true,
      backdrop: true,
      ignoreBackdropClick: false,
      class: 'modal-lg',
    });
  }

  public openModal(template: TemplateRef<any>, fabric: Fabric) {
    this.selectedFabric = fabric;
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
}
