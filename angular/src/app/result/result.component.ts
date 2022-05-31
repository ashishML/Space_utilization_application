import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent implements OnInit {

  constructor(private service: ApiService) { }
  getFrame :any


  ngOnInit(): void {
    this.service.UploadedVideosName.subscribe(res => { 
      this.service.getVideos(res).subscribe((resp:any) => {
        console.log(resp.data);
        this.getFrame = resp.data;
      })
    })
    
  }

}
