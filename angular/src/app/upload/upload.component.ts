import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent implements OnInit {

  constructor() { }
  fileOver = false;
  formData!: FormData;
  fileName: string = '';

  ngOnInit(): void {
  }
  
  uploadFile(event: Event) {
    const element = event.currentTarget as HTMLInputElement;
    let fileList: FileList | null = element.files;
    if (fileList) {
      console.log(fileList[0]);
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
      console.log(fileList[0]);
      this.formData = new FormData();
      this.formData.append('file', fileList[0])
      this.fileName = fileList[0].name
    }
  }

  onDragOver(event:any) {
    this.fileOver = true
    event.preventDefault();
    event.stopPropagation();
  }

  onDragLeave(event:any) {
    this.fileOver = false
    event.preventDefault();
    event.stopPropagation();
  }

}
