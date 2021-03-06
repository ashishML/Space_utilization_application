import { AfterViewInit, Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-annotate',
  templateUrl: './annotate.component.html',
  styleUrls: ['./annotate.component.css']
})
export class AnnotateComponent implements OnInit, AfterViewInit {
  constructor(private service: ApiService, private sanitizer: DomSanitizer, private router: Router, private toastr: ToastrService) { }

  loadingAnimate = true;
  imagePath: any = [];
  cordinates_all: any = [];
  @ViewChildren("multicanvas") multicanvas!: QueryList<ElementRef>;
  canvas_img_info: any = []
  canvasid: any = [];
  public ctx!: CanvasRenderingContext2D;
  newImageObj: any;
  image_dimensions: any = [];
  loading = false;
  fileName = [];

  ngOnInit(): void {
    this.service.UploadedVideosName.subscribe(res => {
      console.log(res, 'uploaded video name');
      this.fileName = res
      this.imagePath = [...this.fileName];
      this.loadingAnimate = true;
      this.service.getFrames(JSON.stringify(this.fileName)).subscribe({
        next: (res: any) => {
          console.log(res, 'get frames');
          this.loadingAnimate = false;
          this.imagePath = [];
          const base64Image: any = [];
          res['data'].forEach((element: any) => {
            this.imagePath.push(this.sanitizer.bypassSecurityTrustUrl(`data:image/jpeg;base64,${element}`))
            base64Image.push(`data:image/jpeg;base64,${element}`)
          });
          base64Image.forEach(async (elements: any) => {
            let img = new Image();
            img.src = elements
            await img.decode();
            this.image_dimensions.push({ img: img, width: img.width, height: img.height })
            this.ngAfterViewInit()
          });
        },
        error: err => this.loadingAnimate = false
      });
    })
    
  }


  ngAfterViewInit() {
    this.canvasid = this.multicanvas.toArray()
    if(this.image_dimensions.length!=0){
      this.canvasid.forEach((element: any) => {
        const ref = document.getElementById(element.nativeElement.id) as HTMLCanvasElement
        this.ctx = ref.getContext('2d') as unknown as CanvasRenderingContext2D;
        let img_width = this.image_dimensions[+element.nativeElement.id]?.img.width;
        let img_height = this.image_dimensions[+element.nativeElement.id]?.img.height;
        ref.width = img_width;
        ref.height = img_height;
        this.ctx.drawImage(this.image_dimensions[+element.nativeElement.id]?.img, 0, 0, img_width, img_height);
        if (this.canvas_img_info.some((i: any) => i.id === +element.nativeElement.id)) {
          return
        } else {
          this.canvas_img_info.push({ ctx: this.ctx, img_info: this.image_dimensions[+element.nativeElement.id], img_width: img_width, img_height: img_height, id: +element.nativeElement.id, cordinates: [] })
        }
      });
    }
  }

  //different approach
  rect(evt: any, id: any) {
    this.canvas_img_info.forEach((element: any) => {
      if (element.id == id) {
        const cordinates = {
          x: NaN, y: NaN, id: NaN, v_name: ''
        }
        let x_cordinate = this.getcordinate(evt.offsetX, element.img_width, element.ctx.canvas.offsetWidth)
        let y_cordinate = this.getcordinate(evt.offsetY, element.img_height, element.ctx.canvas.offsetHeight)
        cordinates.x = x_cordinate
        cordinates.y = y_cordinate
        cordinates.id = id
        cordinates.v_name = this.fileName[id] 
        if (element.cordinates.some((i: any) => i[0] === x_cordinate && i[1] === y_cordinate)) {
          return
        } else {
          element.cordinates.push([x_cordinate, y_cordinate])
          this.cordinates_all.push(cordinates)
        }
        this.drawDot(x_cordinate, y_cordinate, element.ctx)
        if (element.cordinates.length === 4) {
          this.drawPoly(element.cordinates, element.ctx)
        }
      }
    })

  }

  getcordinate(cordinate: any, originalcordinate: any, ratiocordinate: any): any {
    return cordinate * (originalcordinate / ratiocordinate);
  }

  // draw polygon from a list of 4 points
  drawPoly(points: any, ctx: any) {
    ctx.lineWidth = 2
    let split = points.splice(0, 4)
    ctx.beginPath()
    ctx.moveTo(split[0][0], split[0][1])
    for (let i of split.reverse()) ctx.lineTo(i[0], i[1])
    ctx.strokeStyle = "rgba(65,203,43,1)"
    ctx.stroke()
    ctx.fillStyle = "rgba(180,246,120,0.4)"
    ctx.fill()
  }

  // draw a dot.
  drawDot(x: any, y: any, ctx: any) {
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fillStyle = "rgba(65,203,43,1)"
    ctx.fill()

  }

  clearCanvas(id: any) {
    this.canvas_img_info.forEach((element: any) => {
      if (element.id == id) {
        element.ctx.clearRect(0, 0, element.img_width, element.img_width)
        element.ctx.canvas.width = element.img_width;
        element.ctx.canvas.height = element.img_height;
        element.ctx.drawImage(element.img_info.img, 0, 0, element.img_width, element.img_height);
        let cordinates_of_image = this.cordinates_all.filter(function (value: any) { return value.id == id; });
        this.cordinates_all = this.cordinates_all.filter(function (obj: any) { return cordinates_of_image.indexOf(obj) == -1 });
      }
    })
  }


  submit(){
    this.loading = true;
    const sendObj :any= {}
    sendObj.roi = JSON.stringify(this.cordinates_all)
    this.service.sendCordinates(sendObj).subscribe({
      next: (res:any) => {
        console.log(res);
        if(res.status){
          this.service.sendExtractedData.next(res.data)
          this.loading = false;
          this.router.navigate(['../result']);
        }
        else{
          this.loading = false;
          this.toastr.error('Please try again', 'Unable to send');
        }
        
      },
      error : (err) => {
        this.loading = false;
        this.toastr.error('Please try again', 'Unable to send');
      }
    })
  }

}