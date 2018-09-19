import {Component, OnInit, TemplateRef} from '@angular/core';
import {NotificationsService} from 'angular2-notifications';
import {BsModalRef, BsModalService} from 'ngx-bootstrap';
import {User, UserList} from '../_model/user';
import {BackendService} from '../_service/backend.service';
import {ViewChild, ElementRef} from '@angular/core' ;

@Component({
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})

export class UserComponent implements OnInit {
  rows;
  modalRef: BsModalRef;
  loading: boolean;
  loadingMessage: string;
  selectedUser: User;
  users: User[];
  user: User;
  roles: any[];
  editing = {};
  modalMessage = 'Add' ;
  confirmPassword: string ;
  usernameSort:any ;
  userRole:number ;
  userName:string ;
  constructor(private backendService: BackendService, private notificationService: NotificationsService,
    private modalService: BsModalService) {
    this.loadingMessage = 'Loading users';
    this.roles = [
      {'id': 0, name: 'Admin'},
      {'id': 1, name: 'User'},
      {'id': 2, name: 'Blacklist'},
    ];
    this.usernameSort = this.backendService.prefs.username_sort ;
    this.userName = localStorage.getItem('userName') ;
    this.userRole = parseInt(localStorage.getItem('userRole')) ;
  }

  ngOnInit(): void {
    this.getUsers();
   }

   onSort(event) {
     this.backendService.prefs.username_sort = event.sorts ;
   }

  getUsers() {
    this.loading = true;
    this.backendService.getUsers().subscribe((results: UserList) => {
      const objects = results.objects;
      this.users = objects;
      this.rows = objects;
      this.loading = false;
    }, (err) => {
      this.notificationService.error('Error', 'Could not get user list');
      this.loading = false;
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.users.filter(function (d) {
      return d.username.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

  deleteUser() {
    this.modalRef.hide();
    this.loading = true;
    this.backendService.deleteUser(this.selectedUser).subscribe((results) => {
      this.getUsers();
    }, (err) => {
      this.notificationService.error('Error', 'Could not delete user');
      this.loading = false;
    });
  }

  public onSubmit() {
    this.modalRef.hide();
    this.loading = true;
    this.backendService.createUser(this.user).subscribe((results) => {
      this.getUsers();
    }, (err) => {
      this.notificationService.error('Error', 'Could not add user');
      this.loading = false;
    });
  }

  public updateValue() {
    if (this.confirmPassword !== this.user.password) {
      this.notificationService.error('Passwords do not match') ;
      return ;
    }
    this.confirmPassword='' ;
      this.backendService.updateUser(this.user).subscribe((results) => {
        this.notificationService.success('Success', 'Changes saved');
        this.hideModal() ;
        this.getUsers() ;
      }, (err) => {
        this.notificationService.error('Error', 'Could not update user');
        this.loading = false;
      });
    }


  public openAddModal(template: TemplateRef<any>) {
    this.user = new User();
    this.modalRef = this.modalService.show(template, {
      animated: true,
      keyboard: true,
      backdrop: true,
      ignoreBackdropClick: false,
      class: 'modal-lg',
    });
  }

  public openModal(template: TemplateRef<any>, user: User) {
    this.selectedUser = user;
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

  public editMode(template: TemplateRef<any> , user: User) {
    this.user = user ;
    this.confirmPassword = undefined ;
    this.modalRef = this.modalService.show(template, {
      animated: true,
      keyboard: true,
      backdrop: false,
      ignoreBackdropClick: false,
      class: 'modal-lg',
    });
  }
}
