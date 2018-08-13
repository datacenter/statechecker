import {Component, OnInit, TemplateRef, ElementRef, ViewChild, AfterViewInit} from "@angular/core";
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
  confirmPassword: string ;
  fromAddTemplate = false ;
  @ViewChild('editTemplate') editModal: TemplateRef<any> ;

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
    const fromAdd = this.fromAddTemplate ;
    this.fromAddTemplate = false ;
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
            if (fromAdd) {
              this.modalRef.hide() ;
              this.openModal(this.editModal , fabric) ;
            }
          }
        }, (err) => {
          this.notificationService.error('Error', 'Could not get controllers');
          if (fromAdd) {
            this.modalRef.hide() ;
            this.openModal(this.editModal , fabric) ;
          }
        });
      } else {
        this.notificationService.error('Error', results['error']);
        if (fromAdd) {
          this.modalRef.hide() ;
          this.openModal(this.editModal , fabric) ;
        }
      }
    }, (err) => {
      this.notificationService.error('Error', 'Could not verify APIC');
      if (fromAdd) {
        this.modalRef.hide() ;
        this.openModal(this.editModal , fabric) ;
      }
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

  public updateValue() {
    if (this.confirmPassword !== this.fabric.apic_password) {
      this.notificationService.error('Passwords do not match') ;
      return ;
    }
      this.backendService.updateFabric(this.fabric).subscribe((results) => {
        this.notificationService.success('Success', 'Changes saved');
        this.getFabrics(true) ;
      }, (err) => {
        this.notificationService.error('Error', 'Could not update fabric');
        this.loading = false;
      });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.fabrics.filter(function (d) {
      return d.fabric.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

  public openAddModal(template: TemplateRef<any>) {
    this.fabric = new Fabric();
    this.fromAddTemplate = true ;
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
    if (this.editModal === template) {
      this.cloneFabric(fabric) ;
    }
    this.modalRef = this.modalService.show(template, {
      animated: true,
      keyboard: true,
      backdrop: true,
      ignoreBackdropClick: false,
      class: 'modal-lg',
    });
  }

  public cloneFabric(fabric: Fabric) {
    this.fabric = new Fabric() ;
    this.fabric.apic_hostname = fabric.apic_hostname ;
    this.fabric.apic_password = fabric.apic_password ;
    this.fabric.apic_username = fabric.apic_username ;
    this.fabric.controllers = fabric.controllers ;
    this.fabric.fabric = fabric.fabric ;
    this.fabric.apic_cert = fabric.apic_cert ;
  }

  public hideModal() {
    this.modalRef.hide();
  }
}
