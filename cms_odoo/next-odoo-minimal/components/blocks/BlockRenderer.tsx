import HtmlBlock from './HtmlBlock';
import TextBlock from './TextBlock';
import HeadingBlock from './HeadingBlock';
import ImageBlock from './ImageBlock';
import HeroBlock from './HeroBlock';
import UserListBlock from './UserListBlock';

interface BlockData {
  id: number;
  name: string;
  type: string;
  sequence: number;
  [key: string]: any;
}

interface BlockRendererProps {
  block: BlockData;
}

export default function BlockRenderer({ block }: BlockRendererProps) {
  switch (block.type) {
    case 'html':
      return <HtmlBlock content={block.content || ''} />;

    case 'text':
      return <TextBlock content={block.content || ''} />;

    case 'heading':
      return <HeadingBlock text={block.text || ''} level={block.level || 'h2'} />;

    case 'image':
      return <ImageBlock url={block.url || ''} alt={block.alt || ''} />;

    case 'hero':
      return (
        <HeroBlock
          title={block.title || ''}
          subtitle={block.subtitle || ''}
          buttonText={block.buttonText}
          buttonUrl={block.buttonUrl}
          backgroundImage={block.backgroundImage}
        />
      );

    case 'user_list':
      return <UserListBlock users={block.users || []} limit={block.limit} />;

    default:
      console.warn(`Unknown block type: ${block.type}`);
      return (
        <div style={{ padding: '1rem', background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px' }}>
          <strong>Unknown block type:</strong> {block.type}
        </div>
      );
  }
}
