import styles from './ImageBlock.module.scss';

interface ImageBlockProps {
  url: string;
  alt: string;
}

export default function ImageBlock({ url, alt }: ImageBlockProps) {
  return (
    <div className={styles.imageBlock}>
      <img src={url} alt={alt} />
    </div>
  );
}
