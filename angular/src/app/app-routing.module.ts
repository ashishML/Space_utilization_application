import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AnnotateComponent } from './annotate/annotate.component';
import { ResultComponent } from './result/result.component';
import { UploadComponent } from './upload/upload.component';

const routes: Routes = [
  { path: '', redirectTo: '/upload', pathMatch: 'full' },
  {
    path:'upload',
    component:UploadComponent,
  },
  {
    path:'annotate',
    component:AnnotateComponent,
  },
  {
    path:'result',
    component:ResultComponent,
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
