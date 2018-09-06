export class preferences {
    //each variable represents if the field is sorted in ascending natural order.
    fabric_sort:any ;
    snapshot_sort:any ;
    comparison_sort:any ;
    comparisonDetail_accordion:boolean = false ;
    comparisonDetail_classView:boolean = true; // false means nodeview
    comparisonDetail_emptyResults:boolean = false ;
    comparisonDetail_sort:any ;
    comparisonResult_emptyResults:boolean ;
    comparisonResult_sort:any ;
    comparisonResult_modified_lineDiffMode:boolean ; // false means semantic mode
    comparisonResult_modified_emptyResults:boolean ;
    comparisonResultDetailSort:any ;
    comparisonResultDetailemSort:any ;
    definition_sort:any ;
    username_sort:any ;
    public constructor() {
        this.fabric_sort = [{prop:'fabric',dir:'asc'}] ;
        this.snapshot_sort = [{prop:'start_time', dir:'desc'}] ;
        this.comparison_sort = [{prop:'start_time', dir:'desc'}] ;
        this.comparisonDetail_classView = true ;
        this.comparisonDetail_emptyResults = false ;
        this.comparisonResult_modified_lineDiffMode = true ;
        this.comparisonResult_modified_emptyResults = false ;
        this.comparisonResult_sort = [{prop:'classname',dir:'asc'},{prop:'node_id',dir:'asc'}] ;
        this.comparisonResultDetailSort = [{prop: 'attribute', dir: 'asc'}] ;
        this.comparisonResultDetailemSort = [{prop:'attribute',dir:'asc'}] ;
        this.definition_sort = [{prop: 'classname', dir: 'asc'}] ;
        this.username_sort = [{prop: 'username', dir: 'asc'}] ;
    }
}