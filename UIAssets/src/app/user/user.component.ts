import {Component, OnInit, TemplateRef} from '@angular/core';
import {NotificationsService} from 'angular2-notifications';
import {BsModalRef, BsModalService} from 'ngx-bootstrap';
import {User, UserList} from '../_model/user';
import {BackendService} from '../_service/backend.service';

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
  usernameSort: any;
  userRole: number;
  userName: string;
  roles: ({ id: number; name: string })[];

  constructor(private backendService: BackendService, private notificationService: NotificationsService,
              private modalService: BsModalService) {
    this.loadingMessage = 'Loading users';
    this.roles = [
      {'id': 0, name: 'Admin'},
      {'id': 1, name: 'User'},
    ];
    this.usernameSort = this.backendService.prefs.username_sort;
    this.userName = localStorage.getItem('userName');
    this.userRole = parseInt(localStorage.getItem('userRole'));
  }

  ngOnInit(): void {
    this.getUsers();
  }

  onSort(event) {
    this.backendService.prefs.username_sort = event.sorts;
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
    if (this.user.is_new) {
      this.backendService.createUser(this.user).subscribe((results) => {
        this.getUsers();
      }, (err) => {
        this.notificationService.error('Error', 'Could not add user');
        this.loading = false;
      });
    } else {
      this.backendService.updateUser(this.user).subscribe((results) => {
        this.getUsers();
      }, (err) => {
        this.notificationService.error('Error', 'Could not update user');
        this.loading = false;
      });
    }
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
    this.user = new User(
      user.username,
      user.role,
      user.password,
      user.last_login,
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
