import {Component, OnInit} from "@angular/core";
import {NotificationsService} from "angular2-notifications";
import {BsModalService} from "ngx-bootstrap";
import {Definition, DefinitionList} from "../_model/definition";
import {BackendService} from "../_service/backend.service";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  templateUrl: './definition-detail.component.html',
  styleUrls: ['./definition-detail.component.css']
})

export class DefinitionDetailComponent implements OnInit {
  rows;
  loading: boolean;
  loadingMessage: string;
  definition: Definition;
  managed_objects: any[];

  constructor(private backendService: BackendService, private notificationService: NotificationsService, private modalService: BsModalService, public router: Router, private activatedRoute: ActivatedRoute) {
    this.loadingMessage = 'Loading definition';
  }

  ngOnInit(): void {
    this.getDefinition();
  }

  getDefinition() {
    this.loading = true;
    this.activatedRoute.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id != null) {
        this.backendService.getDefinition(id).subscribe((results: DefinitionList) => {
          let managed_objects = [];
          for (let managed_object of results.objects[0].managed_objects) {
            const moEntry = {'name': managed_object};
            managed_objects.push(moEntry);
          }
          this.managed_objects = managed_objects;
          this.rows = managed_objects;
          this.loading = false;
        }, (err) => {
          this.notificationService.error('Error', 'Could not get definition');
          this.loading = false;
        });
      }
    });
  }

  updateFilter(event) {
    const val = event.target.value.toLowerCase();
    this.rows = this.managed_objects.filter(function (d) {
      return d.name.toLowerCase().indexOf(val) !== -1 || !val;
    });
  }

}
