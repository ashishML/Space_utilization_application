import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from '../api.service';
@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {

  constructor(private service: ApiService, private router: Router, private toastr: ToastrService) { }
  fileName: any = [];
  formData = new FormData();
  loading = false;
  ngOnInit(): void {
  }
  
  uploadFile(event: any) {
    this.fileName = [];  
    const files: FileList  = event.target.files;
    for (let i = 0; i < files.length; i++) {
      this.formData.append(i.toString(), files[i]);
      this.fileName.push(files[i].name);
    }
  }

  onDrop(event: any) {
    event.preventDefault();
    event.stopPropagation();
    this.fileName = [];
    const files: FileList = event.dataTransfer.files;
    for (let i = 0; i < files.length; i++) {
      this.formData.append(i.toString(), files[i]);
      this.fileName.push(files[i].name);
    }
  }

  onDragOver(event:any) {
    event.preventDefault();
    event.stopPropagation();
  }

  onDragLeave(event:any) {
    event.preventDefault();
    event.stopPropagation();
  }

  submitVideo(){
    if (this.fileName.length > 0) {
      this.loading = true;
      this.service.uploadVideo(this.formData).subscribe({
        next: (res:any) => {         
          this.service.UploadedVideosName.next(this.fileName)
            this.loading = false;
            this.router.navigate(['../annotate']);
        },
        error: (error:any) => {
          this.toastr.error('Please try again', 'Unable to send');
          this.loading = false;
        }
      })
    } 
    else {
      this.toastr.error('File Error', 'No file uploaded');
    }
    
  }
  
}
