import { DomSanitizer } from '@angular/platform-browser';
import { ApiService } from '../api.service';
import { AfterViewInit, Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from '@angular/core';

@Component({
  selector: 'app-annotate',
  templateUrl: './annotate.component.html',
  styleUrls: ['./annotate.component.css']
})
export class AnnotateComponent implements OnInit, AfterViewInit {

  constructor(private service: ApiService, private sanitizer: DomSanitizer) { }

  loadingAnimate = true;
  imagePath: any = ['',''];

  cordinates_all: any = [];
  image: any = '../../assets/demo.jpg';
  array_images = ['../../assets/demo.jpg', '../../assets/demo1.jpg']
  @ViewChildren("multicanvas") multicanvas!: QueryList<ElementRef>;
  canvas_img_info: any = []
  canvasid: any = [];
  public ctx!: CanvasRenderingContext2D;
  newImageObj:any;

  ngOnInit(): void {
    this.loadingAnimate = true;
    this.service.getFrames().subscribe({
      next: (res:any) => {
        this.loadingAnimate = false;
        this.imagePath = [];
        const base64Image:any = [];
        res['data'].forEach((element:any) => {
          this.imagePath.push(this.sanitizer.bypassSecurityTrustUrl(`data:image/jpeg;base64,${element}`))
          base64Image.push(`data:image/jpeg;base64,${element}`)
        });
        base64Image.forEach(async(elements:any )=> {
          console.log(elements);
          let img = new Image();
          img.src = elements
          await img.decode();
          console.log(img.width, img.height);
        });        
      },
      error: err => this.loadingAnimate = false
    });
  }


  ngAfterViewInit() {
    this.canvasid = this.multicanvas.toArray()
    this.canvasid.forEach((element: any) => {
      const ref = document.getElementById(element.nativeElement.id) as HTMLCanvasElement
      const img = new Image();
      img.src = this.imagePath[+element.nativeElement.id];
      this.ctx = ref.getContext('2d') as unknown as CanvasRenderingContext2D;
      let img_width = img.width;
      let img_height = img.height;
      ref.width = img_width;
      ref.height = img_height;

      img.onload = () => {
        this.ctx.drawImage(img, 0, 0, img_width, img_height);
      }
      this.canvas_img_info.push({ ctx: this.ctx, img: img.src, img_width: img_width, img_height: img_height, id: +element.nativeElement.id, cordinates: [] })

    });
  }

  //different approach
  rect(evt: any, id: any) {
    for (let x = 0; x < this.canvas_img_info.length; x++) {
      if (this.canvas_img_info[x].id == id) {
        const cordinates = {
          x: null, y: null, id: null
        }
        let x_cordinate = this.getcordinate(evt.offsetX, this.canvas_img_info[x].img_width, this.canvas_img_info[x].ctx.canvas.offsetWidth)
        let y_cordinate = this.getcordinate(evt.offsetY, this.canvas_img_info[x].img_height, this.canvas_img_info[x].ctx.canvas.offsetHeight)
        cordinates.x = x_cordinate
        cordinates.y = y_cordinate
        cordinates.id = id
        this.cordinates_all.push(cordinates)
        this.canvas_img_info[x].cordinates.push([x_cordinate, y_cordinate])
        console.log(this.canvas_img_info[x].cordinates)
        this.drawDot(x_cordinate, y_cordinate, this.canvas_img_info[x].ctx)
        if (this.canvas_img_info[x].cordinates.length === 4) {

          this.drawPoly(this.canvas_img_info[x].cordinates, this.canvas_img_info[x].ctx)
        }

      }
    }

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
    ctx.stroke()

  }

  // draw a dot.
  drawDot(x: any, y: any, ctx: any) {
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fill()
  }
  
}
