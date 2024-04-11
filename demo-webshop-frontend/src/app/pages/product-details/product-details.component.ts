import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, Subscription, delay } from 'rxjs';
import { PRODUCTS } from 'src/app/constants/products';
import { Product } from 'src/app/models/product';
import { DataService } from './../../services/data.service';
import { Data } from 'src/app/models/data';
import { User } from 'src/app/models/user';


@Component({
  templateUrl: './product-details.component.html',
  styleUrls: ['./product-details.component.scss']
})
export class ProductDetailsComponent implements OnInit, OnDestroy {
  product: Product | undefined;
  isMainSidenavOpen$: Observable<boolean>;
  subscription: Subscription;

  constructor(
    private route: ActivatedRoute,
    private dataService: DataService
  ) { }

  ngOnInit(): void {
    const productId = this.route.snapshot.paramMap.get('id');
    this.product = PRODUCTS.find((f) => f.id === productId);

    this.isMainSidenavOpen$ = this.dataService.isSidenavOpen$.asObservable();
  }

  sendData(): void {
    if (!this.product) return;
    const user: User = this.dataService.user;
    let payload: Data;
    const productId = this.product.id;

    this.dataService.getIpAddress().subscribe((ip) => {
      payload = {
        timestamps: [new Date().getTime() * 1000000],
        stringValues: {
          'userId': [user.userId],
          'age': [user.age.toString()],
          'gender': [user.gender],
          'ip': [ip],
          'userAgent': [navigator.userAgent],
          'productId': [productId],
        }
      };
    });

  }

  clearSelection(): void {
    this.dataService.categorySelection = [];
  }

  ngOnDestroy(): void {
  }
}
