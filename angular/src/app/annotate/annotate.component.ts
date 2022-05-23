import { Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-annotate',
  templateUrl: './annotate.component.html',
  styleUrls: ['./annotate.component.css']
})
export class AnnotateComponent implements OnInit {

  constructor(private service: ApiService, private sanitizer: DomSanitizer) { }

  loadingAnimate = true;
  imagePath: any = ['',''];

  ngOnInit(): void {
    this.loadingAnimate = true;
    this.service.getFrames().subscribe({
      next: (res:any) => {
        this.loadingAnimate = false;
        this.imagePath = [];
        console.log(res);
        res['data'].forEach((element:any) => {
          this.imagePath.push(this.sanitizer.bypassSecurityTrustUrl(`data:image/jpeg;base64,${element}`))
        });
      },
      error: err => this.loadingAnimate = false
    });
  }

  
}
