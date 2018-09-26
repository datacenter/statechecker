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
  fabrics: Fabric[];
  fabricSorts: any;
  userRole: number;

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
              private modalService: BsModalService) {
    this.loadingMessage = 'Loading fabrics';
    this.fabricSorts = this.backendService.prefs.fabric_sort;
    this.userRole = parseInt(localStorage.getItem('userRole'));
  }

  ngOnInit(): void {
    this.getFabrics();
  }

  onSort(event) {
    this.backendService.prefs.fabric_sort = event.sorts;
  }

  getFabrics() {
    this.loading = true;
    this.backendService.getFabrics().subscribe((results: FabricList) => {
      this.fabrics = results.objects;
      this.rows = results.objects;
      this.loading = false;
    }, (err) => {
      if (err['error'] !== undefined && err['error']['error'] !== undefined) {
        this.notificationService.error(err['error']['error']);
      } else {
        this.notificationService.error('Error', 'Could not get fabric list');
      }
      this.loading = false;
    });
  }

  verifyFabric(fabric: Fabric) {
    const oldLoadingMessage = this.loadingMessage;
    this.loadingMessage = 'Validating fabric ' + fabric.fabric;
    this.loading = true;
    this.backendService.verifyFabric(fabric).subscribe((results) => {
      if (results['success']) {
        this.notificationService.success('Success', 'Credentials validated, fetching controllers');
        this.backendService.updateFabricControllers(fabric).subscribe((results) => {
          if (results['success']) {
            this.notificationService.success('Success', 'Controllers fetched');
            this.loadingMessage = oldLoadingMessage;
            this.getFabrics();
          } else {
            this.notificationService.error('Error', results['error']);
            this.loading = false;
            this.loadingMessage = oldLoadingMessage;
          }
        }, (err) => {
          this.notificationService.error('Error', 'Could not get controllers');
          this.loading = false;
          this.loadingMessage = oldLoadingMessage;
        });
      } else {
        this.notificationService.error('Error', results['error']);
        this.loading = false;
        this.loadingMessage = oldLoadingMessage;
      }
    }, (err) => {
      this.notificationService.error('Error', 'Could not verify APIC');
      this.loading = false;
      this.loadingMessage = oldLoadingMessage;
    });
  }

  deleteFabric() {
    this.loading = true;
    this.backendService.deleteFabric(this.selectedFabric).subscribe((results) => {
      this.hideModal();
      this.getFabrics();
    }, (err) => {
      if (err['error'] !== undefined && err['error']['error'] !== undefined) {
        this.notificationService.error(err['error']['error']);
      } else {
        this.notificationService.error('Error', 'Could not delete fabric');
      }
      this.loading = false;
    });
  }

  public onSubmit() {
    this.hideModal();
    const validate = this.fabric.validate;
    if (this.fabric.is_new) {
      this.backendService.createFabric(this.fabric).subscribe((results) => {
        if (validate) {
          this.verifyFabric(this.fabric);
        } else {
          this.getFabrics();
        }
      }, (err) => {
        if (err['error'] !== undefined && err['error']['error'] !== undefined) {
          this.notificationService.error(err['error']['error']);
        } else {
          this.notificationService.error('Error', 'Could not add fabric');
        }
        this.loading = false;
      });
    } else {
      this.backendService.updateFabric(this.fabric).subscribe((results) => {
        if (validate) {
          this.verifyFabric(this.fabric);
        } else {
          this.getFabrics();
        }
      }, (err) => {
        if (err['error'] !== undefined && err['error']['error'] !== undefined) {
          this.notificationService.error(err['error']['error']);
        } else {
          this.notificationService.error('Error', 'Could not update fabric');
        }
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
    this.fabric = new Fabric(
      fabric.apic_cert,
      fabric.apic_hostname,
      fabric.apic_username,
      fabric.apic_password,
      fabric.controllers,
      fabric.fabric,
      false,
      false
    );
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
