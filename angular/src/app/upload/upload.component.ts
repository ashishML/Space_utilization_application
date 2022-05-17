import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {

  constructor() { }
  fileOver = false;
  formData: FormData | any;
  fileName: string = '';

  ngOnInit(): void {
  }
  
  uploadFile(event: Event) {
    const element = event.currentTarget as HTMLInputElement;
    let fileList: FileList | null = element.files;
    if (fileList) {
      console.log("FileUpload -> files", fileList[0]);
      this.formData = new FormData();
      this.formData.append('file', fileList[0])
      this.fileName = fileList[0].name
    }
  }

  onDrop(event: any) {
    event.preventDefault();
    event.stopPropagation();
    let fileList: FileList | null = event.dataTransfer.files;
    if (fileList) {
      console.log("FileUpload -> files", fileList[0]);
      this.formData = new FormData();
      this.formData.append('file', fileList[0])
      this.fileName = fileList[0].name
    }
  }

  onDragOver(evt:any) {
    this.fileOver = true
    evt.preventDefault();
    evt.stopPropagation();
  }

  onDragLeave(evt:any) {
    this.fileOver = false
    evt.preventDefault();
    evt.stopPropagation();
  }

}
