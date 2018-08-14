import {Injectable} from '@angular/core';
import {HttpClient, HttpParams, HttpRequest, HttpEvent, HttpEventType } from '@angular/common/http';
import {User, UserList} from '../_model/user';
import {Definition, DefinitionList} from '../_model/definition';
import {Fabric, FabricList} from '../_model/fabric';
import {Snapshot, SnapshotList} from '../_model/snapshot';
import {Comparison, ComparisonList} from '../_model/comparison';
import {Page} from '../_model/page';
import {ComparisonResultList} from '../_model/comparison-result';
import {Observable} from 'rxjs/Observable';
import {environment} from '../../environments/environment';
import {ManagedObjectList} from '../_model/managed-object';


@Injectable()
export class BackendService {
  private baseUrl = '';
  public app_status = 'starting app components' ;
  constructor(private http: HttpClient) {
    if (!environment.app_mode) {
      this.baseUrl = environment.api_entry;
    }
  }


  login(username, password): Observable<any> {
    return this.http.post(this.baseUrl + 'users/login', {'username': username, 'password': password});
  }

  logout(): Observable<any> {
    return this.http.post(this.baseUrl + 'users/logout', {});
  }

  getUsers(): Observable<UserList> {
    const options = {
      params: new HttpParams().set('sort', 'username|asc')
    };
    return this.http.get<UserList>(this.baseUrl + 'users', options);
  }

  createUser(user: User): Observable<any> {
    return this.http.post(this.baseUrl + 'users', user);
  }

  updateUser(user: User): Observable<any> {
    if (user.role === 'Admin') {
      user.role = 0;
    } else if (user.role === 'User') {
      user.role = 1;
    } else if (user.role === 'Blacklist') {
      user.role = 2;
    }
    delete user.last_login;
    return this.http.patch(this.baseUrl + 'users/' + user.username, user);
  }

  deleteUser(user: User): Observable<any> {
    return this.http.delete(this.baseUrl + 'users/' + user.username);
  }

  getDefinitions(): Observable<DefinitionList> {
    const options = {
      params: new HttpParams().set('sort', 'classname|asc')
    };
    return this.http.get<DefinitionList>(this.baseUrl + 'aci/definitions', options);
  }

  getDefinition(definitionName: string): Observable<DefinitionList> {
    return this.http.get<DefinitionList>(this.baseUrl + 'aci/definitions/' + definitionName);
  }

  createDefinition(definition: Definition): Observable<any> {
    return this.http.post(this.baseUrl + 'aci/definitions', definition);
  }

  deleteDefinition(definition: Definition): Observable<any> {
    return this.http.delete(this.baseUrl + 'aci/definitions/' + definition.definition);
  }

  getManagedObjects(): Observable<ManagedObjectList> {
    const options = {
      params: new HttpParams().set('sort', 'classname|asc')
    };
    return this.http.get<ManagedObjectList>(this.baseUrl + 'aci/mo', options);
  }

  getManagedObject(managedObject: String): Observable<ManagedObjectList> {
    return this.http.get<ManagedObjectList>(this.baseUrl + 'aci/mo/' + managedObject);
  }

  verifyFabric(fabric: Fabric): Observable<any> {
    return this.http.post(this.baseUrl + 'aci/fabrics/' + fabric.fabric + '/verify', {});
  }

  updateFabricControllers(fabric: Fabric): Observable<any> {
    return this.http.post(this.baseUrl + 'aci/fabrics/' + fabric.fabric + '/controllers', {});
  }

  createFabric(fabric: Fabric): Observable<any> {
    return this.http.post(this.baseUrl + 'aci/fabrics', fabric);
  }

  getFabrics(): Observable<FabricList> {
    const options = {
      params: new HttpParams().set('sort', 'fabric|asc')
    };
    return this.http.get<FabricList>(this.baseUrl + 'aci/fabrics', options);
  }

  updateFabric(fabric: Fabric): Observable<any> {
    delete fabric.controllers;
    return this.http.patch(this.baseUrl + 'aci/fabrics/' + fabric.fabric, fabric);
  }

  deleteFabric(fabric: Fabric): Observable<any> {
    return this.http.delete(this.baseUrl + 'aci/fabrics/' + fabric.fabric);
  }

  createSnapshot(snapshot: Snapshot): Observable<any> {
    delete snapshot['fabric_obj'];
    return this.http.post(this.baseUrl + 'aci/snapshots', snapshot);
  }

  getSnapshots(timestamp: boolean = false): Observable<SnapshotList> {
    let params = new HttpParams();
    if (!timestamp) {
      params = params.set('sort', 'fabric|asc,description|asc');
    } else {
      params = params.set('sort', 'start_time|asc');
    }
    const options = {
      params: params
    };
    return this.http.get<SnapshotList>(this.baseUrl + 'aci/snapshots', options);
  }

  getSnapshot(id): Observable<SnapshotList> {
    return this.http.get<SnapshotList>(this.baseUrl + 'aci/snapshots/' + id);
  }

  deleteSnapshot(snapshot: Snapshot): Observable<any> {
    return this.http.delete(this.baseUrl + 'aci/snapshots/' + snapshot._id);
  }

  createComparison(comparison: Comparison): Observable<any> {
    delete comparison['snapshot1_obj'];
    delete comparison['snapshot2_obj'];
    return this.http.post(this.baseUrl + 'aci/compare', comparison);
  }

  getComparisons(): Observable<ComparisonList> {
    const options = {
      params: new HttpParams().set('sort', 'start_time|desc')
    };
    return this.http.get<ComparisonList>(this.baseUrl + 'aci/compare', options);
  }

  getComparison(id): Observable<ComparisonList> {
    return this.http.get<ComparisonList>(this.baseUrl + 'aci/compare/' + id);
  }

  deleteComparison(comparison: Comparison): Observable<any> {
    return this.http.delete(this.baseUrl + 'aci/compare/' + comparison._id);
  }

  getComparisonResults(comparison: Comparison, page: Page, key: string, value: string,
    includeEmpty: boolean, sorts): Observable<ComparisonResultList> {
    let params = new HttpParams();
    params = params
      .set('page', page.pageNumber.toString())
      .set('page-size', page.size.toString())
    ;
    if (sorts.length > 0) {
      let sortParts = [];
      for (let sort of sorts) {
        sortParts.push('total.' + sort['prop'] + '|' + sort['dir']);
      }
      params = params.set('sort', sortParts.join(','));
    }
    params = params.set('include', 'total,compare_id,classname,node_id');
    if (key === 'class') {
      if (!includeEmpty) {
        params = params
          .set('filter', 'and(and(eq("compare_id","' + comparison._id + '"),regex("classname","(?i)^' + value + '")),or(gt("total.created",0),gt("total.deleted",0),gt("total.modified",0)))');
      } else {
        params = params
          .set('filter', 'and(eq("compare_id","' + comparison._id + '"),regex("classname","(?i)^' + value + '"))');
      }
    } else if (key === 'node') {
      if (!includeEmpty) {
        params = params
          .set('filter', 'and(and(eq("compare_id","' + comparison._id + '"),eq("node_id",' + value + ')),or(gt("total.created",0),gt("total.deleted",0),gt("total.modified",0)))');
      } else {
        params = params
          .set('filter', 'and(eq("compare_id","' + comparison._id + '"),eq("node_id",' + value + '))');
      }
    }
    const options = {
      params: params
    };
    return this.http.get<ComparisonResultList>(this.baseUrl + 'aci/compare/results', options);
  }

  getComparisonResultsDetails(comparison: Comparison, key: string, value: string, subkey: string, subvalue: string, type: string): Observable<ComparisonResultList> {
    let params = new HttpParams();
    params = params.set('include', type);
    if (key === 'class') {
      params = params
        .set('filter', 'and(eq("compare_id","' + comparison._id + '"),regex("classname","(?i)^' + value + '"),eq("node_id",' + subvalue + '))')
      ;
    } else if (key === 'node') {
      params = params
        .set('filter', 'and(eq("compare_id","' + comparison._id + '"),eq("node_id",' + value + '),eq("classname","' + subvalue + '"))')
      ;
    }
    const options = {
      params: params
    };
    return this.http.get<ComparisonResultList>(this.baseUrl + 'aci/compare/results', options);
  }

  getProgressFor(type: string, id: string) {
  const url = this.baseUrl + '/aci/' + type + '/' + id + '?include=progress,status' ;
  const httpCopy = this.http ;
  return Observable.interval(1000).switchMap(() => httpCopy.get(url).map((data: Response) => data)) ;
  }

  downloadSnapshot(id , filepath) {
    const url = this.baseUrl + 'aci/snapshots/' + id + '/download' ;
    const path = filepath.split('/') ;

    return this.http.get(url, {responseType: 'blob'}).map( (data) => {
      return {
        data: data,
        filename: path[path.length - 1]
      } ;
    }) ;
  }

  uploadSnapshot(filedata) {
    const currentTime = new Date() ;
    const url = this.baseUrl  + 'aci/snapshots/' +  'upload' ;
    return this.http.post(url, filedata, {reportProgress: true}) ;
  }

}
