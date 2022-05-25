import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent implements OnInit {

  constructor(private api: ApiService) { }
  getFrame :any

  ngOnInit(): void {
    console.log(this.api.getVideos());
    this.getFrame = this.api.getVideos()
  }

}
