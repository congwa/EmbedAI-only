/**
 * 商品卡片组件
 */
import React from 'react'
import { ProductRecommendation, IntelliRecsConfig } from '../types'

interface ProductCardProps {
  product: ProductRecommendation
  onClick: () => void
  config: IntelliRecsConfig
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onClick,
  config
}) => {
  const formatPrice = (price: number, currency: string) => {
    if (currency === 'CNY') {
      return `¥${price.toFixed(2)}`
    }
    return `${currency} ${price.toFixed(2)}`
  }

  const renderRating = (rating?: number) => {
    if (!rating) return null
    
    const stars = Math.round(rating * 2) / 2 // 四舍五入到0.5
    const fullStars = Math.floor(stars)
    const hasHalfStar = stars % 1 !== 0

    return (
      <div className="intellirecs-rating">
        <div className="intellirecs-stars">
          {Array.from({ length: 5 }, (_, i) => (
            <span
              key={i}
              className={`intellirecs-star ${
                i < fullStars
                  ? 'full'
                  : i === fullStars && hasHalfStar
                  ? 'half'
                  : 'empty'
              }`}
            >
              ★
            </span>
          ))}
        </div>
        <span className="intellirecs-rating-text">{rating.toFixed(1)}</span>
      </div>
    )
  }

  return (
    <div className="intellirecs-product-card" onClick={onClick}>
      {/* 商品图片 */}
      <div className="intellirecs-product-image">
        {product.imageUrl ? (
          <img
            src={product.imageUrl}
            alt={product.title}
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.style.display = 'none'
              target.nextElementSibling?.classList.remove('hidden')
            }}
          />
        ) : null}
        
        {/* 占位图标 */}
        <div className={`intellirecs-image-placeholder ${product.imageUrl ? 'hidden' : ''}`}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <rect
              x="3"
              y="3"
              width="18"
              height="18"
              rx="2"
              ry="2"
              stroke="currentColor"
              strokeWidth="2"
            />
            <circle cx="8.5" cy="8.5" r="1.5" stroke="currentColor" strokeWidth="2" />
            <path
              d="M21 15l-5-5L5 21"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {/* 库存状态 */}
        {product.stock !== undefined && (
          <div className={`intellirecs-stock-badge ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}`}>
            {product.stock > 0 ? '有货' : '缺货'}
          </div>
        )}
      </div>

      {/* 商品信息 */}
      <div className="intellirecs-product-info">
        <div className="intellirecs-product-title" title={product.title}>
          {product.title}
        </div>

        {/* 品牌和类目 */}
        {(product.brand || product.category) && (
          <div className="intellirecs-product-meta">
            {product.brand && (
              <span className="intellirecs-product-brand">{product.brand}</span>
            )}
            {product.category && (
              <span className="intellirecs-product-category">{product.category}</span>
            )}
          </div>
        )}

        {/* 价格 */}
        <div className="intellirecs-product-price">
          {formatPrice(product.price, product.currency)}
        </div>

        {/* 评分 */}
        {renderRating(product.rating)}

        {/* 推荐理由 */}
        {product.reasons && product.reasons.length > 0 && (
          <div className="intellirecs-product-reasons">
            {product.reasons.slice(0, 3).map((reason, index) => (
              <span key={index} className="intellirecs-reason-tag">
                {reason}
              </span>
            ))}
          </div>
        )}

        {/* 商品标签 */}
        {product.tags && product.tags.length > 0 && (
          <div className="intellirecs-product-tags">
            {product.tags.slice(0, 3).map((tag, index) => (
              <span key={index} className="intellirecs-product-tag">
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 点击指示器 */}
      <div className="intellirecs-card-action">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path
            d="M7 17L17 7M17 7H7M17 7v10"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  )
}
