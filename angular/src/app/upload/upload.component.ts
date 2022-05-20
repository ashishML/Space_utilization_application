import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {

  constructor(private service: ApiService) { }
  fileName: any = [];
  formData = new FormData();

  ngOnInit(): void {
  }
  
  uploadFile(event: any) {
    this.fileName = [];  
    const files: FileList  = event.target.files;
    for (let i = 0; i < files.length; i++) {
      this.formData.append("file[]", files[i]);
      this.fileName.push(files[i].name);
    }
    
  }

  onDrop(event: any) {
    event.preventDefault();
    event.stopPropagation();
    this.fileName = [];
    const files: FileList = event.dataTransfer.files;
    for (let i = 0; i < files.length; i++) {
      this.formData.append("file[]", files[i]);
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
    this.service.uploadVideo(this.formData).subscribe(
      res => { console.log(res)},
    )
  }
}
