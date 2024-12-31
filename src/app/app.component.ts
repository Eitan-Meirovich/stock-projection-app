import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockProjectionComponent } from './stock-projection/stock-projection.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, StockProjectionComponent],
  template: `
    <app-stock-projection></app-stock-projection>
  `,
  styleUrls: ['./app.component.css']
})
export class AppComponent { }