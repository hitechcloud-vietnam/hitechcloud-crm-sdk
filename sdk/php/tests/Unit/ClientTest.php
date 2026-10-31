<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Tests\Unit;

use HiTechCloud\CRM\Client;
use HiTechCloud\CRM\Resources\Resource;
use HiTechCloud\CRM\Resources\Files;
use HiTechCloud\CRM\Webhook;
use PHPUnit\Framework\TestCase;

final class ClientTest extends TestCase
{
    private function client(): Client
    {
        return new Client([
            'token' => 'crm_at_test',
            'sandbox' => true,
        ]);
    }

    public function testExposesCrudResources(): void
    {
        $crm = $this->client();
        $this->assertInstanceOf(Resource::class, $crm->contacts());
        $this->assertInstanceOf(Resource::class, $crm->customFields());
        $this->assertInstanceOf(Resource::class, $crm->leadSources());
        $this->assertInstanceOf(Files::class, $crm->files());
    }

    public function testBulkGuard(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->client()->companies()->bulk([['op' => 'create', 'data' => []]]);
    }

    public function testWebhookSignatureRoundtrip(): void
    {
        $secret = 'whsec_6b3c15aa';
        $body = '{"event":"deal.won","id":"evt_1"}';
        $sig = Webhook::computeSignature($body, $secret);
        $this->assertTrue(Webhook::verifySignature($body, $sig, $secret));
        $this->assertFalse(Webhook::verifySignature($body, 'deadbeef', $secret));
        $this->assertFalse(Webhook::verifySignature($body, '', $secret));
    }
}
